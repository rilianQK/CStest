import os
import h5py
import numpy as np
import inspect
from abc import ABC


class Serializable(ABC):
    """Mixin class for reading and writing to file using h5py."""
    
    def __str__(self):
        """Generate a string representation of the object by concatenating its initialized attributes (excluding None values) in the format "key: value", with each attribute on a new line."""
        init_params = get_init_params(self)
        lines = []
        for param in init_params:
            value = getattr(self, param, None)
            if value is not None:
                lines.append(f"{param}: {value}")
        return "\n".join(lines)
    
    def __eq__(self, other):
        """Compare two objects of the same class for equality by checking if their initialization parameters are equal, including handling NumPy arrays with `np.allclose`."""
        if not isinstance(other, self.__class__):
            return False
        
        self_params = get_init_params(self)
        other_params = get_init_params(other)
        
        if set(self_params) != set(other_params):
            return False
        
        for param in self_params:
            self_val = getattr(self, param)
            other_val = getattr(other, param)
            
            if isinstance(self_val, np.ndarray) and isinstance(other_val, np.ndarray):
                if not np.allclose(self_val, other_val):
                    return False
            elif self_val != other_val:
                return False
        
        return True
    
    def __new__(cls, *args, **kwargs):
        """Records which parameters should be saved so they can be passed to init."""
        instance = super().__new__(cls)
        return instance
    
    def serialize(self):
        """Serialize a class so that it is ready to be written.

        This method creates nested dictionaries appropriate for writing to h5 files.
        Importantly, we save metadata associated with the class itself and any classes
        it takes as input so that they can be reinstantiated later.

        Returns:
            initdata: Dictionary of data to save, in a format appropriate to pass to h5
        """
        init_params = get_init_params(self)
        serialized_data = {}
        
        for param in init_params:
            value = getattr(self, param)
            
            if hasattr(value, 'serialize'):
                serialized_data[param] = value.serialize()
            elif isinstance(value, np.ndarray):
                serialized_data[param] = value
            elif isinstance(value, (int, float, str, bool, list, tuple, dict)):
                serialized_data[param] = value
            elif value is None:
                serialized_data[param] = None
            else:
                raise ValueError(f"Cannot serialize parameter {param} of type {type(value)}")
        
        serialized_data['__class__'] = self.__class__.__name__
        serialized_data['__module__'] = self.__class__.__module__
        
        return serialized_data
    
    def write_to_file(self, filepath, data_dict):
        """Write a class and associated data to file.

        The goal is to be able to read back both the data that was saved and all of the
        data necessary to reinitialize the class.

        Parameters:
            filepath: Path to the file where we want to save the data. Must be an h5 or
                h5py file
            data_dict: Dictionary containing various raw data to save
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with h5py.File(filepath, 'w') as f:
            # Save class serialization data
            class_data = self.serialize()
            class_group = f.create_group('class_data')
            
            for key, value in class_data.items():
                if isinstance(value, np.ndarray):
                    class_group.create_dataset(key, data=value)
                elif isinstance(value, (int, float, str, bool)):
                    class_group.attrs[key] = value
                elif isinstance(value, dict):
                    subgroup = class_group.create_group(key)
                    for subkey, subvalue in value.items():
                        if isinstance(subvalue, np.ndarray):
                            subgroup.create_dataset(subkey, data=subvalue)
                        elif isinstance(subvalue, (int, float, str, bool)):
                            subgroup.attrs[subkey] = subvalue
                elif value is None:
                    class_group.attrs[key] = 'None'
            
            # Save additional data
            data_group = f.create_group('data')
            for key, value in data_dict.items():
                if isinstance(value, np.ndarray):
                    data_group.create_dataset(key, data=value)
                elif isinstance(value, (int, float, str, bool)):
                    data_group.attrs[key] = value
                elif isinstance(value, dict):
                    subgroup = data_group.create_group(key)
                    for subkey, subvalue in value.items():
                        if isinstance(subvalue, np.ndarray):
                            subgroup.create_dataset(subkey, data=subvalue)
                        elif isinstance(subvalue, (int, float, str, bool)):
                            subgroup.attrs[subkey] = subvalue


def generate_file_path(path, file_name, extension):
    """Generate a unique file path within a specified directory by appending a numeric prefix to the given file name to avoid conflicts, ensuring the directory exists. The numeric prefix is determined by the highest existing prefix in the directory, incremented by one, and formatted with leading zeros.
    Ensure the path exists."""
    os.makedirs(path, exist_ok=True)
    
    existing_files = [f for f in os.listdir(path) if f.endswith(extension)]
    existing_prefixes = []
    
    for filename in existing_files:
        try:
            prefix = filename.split('_')[0]
            if prefix.isdigit():
                existing_prefixes.append(int(prefix))
        except (IndexError, ValueError):
            continue
    
    if existing_prefixes:
        next_prefix = max(existing_prefixes) + 1
    else:
        next_prefix = 0
    
    prefix_str = f"{next_prefix:04d}"
    filename = f"{prefix_str}_{file_name}{extension}"
    return os.path.join(path, filename)


def read_from_file(filepath):
    """Read a class and associated data from file.

    Parameters:
        filepath: Path to the file containing both raw data and the information needed
            to reinitialize our class

    Returns:
        new_class_instance: Class that inherits from Serializable that was earlier
            written with its method write_to_file
        data_dict: Dictionary of data that was passed to write_to_file at the time
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filepath} not found")
    
    data_dict = {}
    
    with h5py.File(filepath, 'r') as f:
        # Read class data
        class_group = f['class_data']
        class_data = {}
        
        for key in class_group.keys():
            if isinstance(class_group[key], h5py.Dataset):
                class_data[key] = np.array(class_group[key])
            elif isinstance(class_group[key], h5py.Group):
                subgroup_data = {}
                for subkey in class_group[key].keys():
                    if isinstance(class_group[key][subkey], h5py.Dataset):
                        subgroup_data[subkey] = np.array(class_group[key][subkey])
                    else:
                        subgroup_data[subkey] = class_group[key].attrs[subkey]
                class_data[key] = subgroup_data
            else:
                class_data[key] = class_group.attrs[key]
        
        for attr_key in class_group.attrs:
            if attr_key not in class_data:
                value = class_group.attrs[attr_key]
                if value == 'None':
                    class_data[attr_key] = None
                else:
                    class_data[attr_key] = value
        
        # Read additional data
        if 'data' in f:
            data_group = f['data']
            for key in data_group.keys():
                if isinstance(data_group[key], h5py.Dataset):
                    data_dict[key] = np.array(data_group[key])
                elif isinstance(data_group[key], h5py.Group):
                    subgroup_data = {}
                    for subkey in data_group[key].keys():
                        if isinstance(data_group[key][subkey], h5py.Dataset):
                            subgroup_data[subkey] = np.array(data_group[key][subkey])
                        else:
                            subgroup_data[subkey] = data_group[key].attrs[subkey]
                    data_dict[key] = subgroup_data
                else:
                    data_dict[key] = data_group.attrs[key]
            
            for attr_key in data_group.attrs:
                if attr_key not in data_dict:
                    value = data_group.attrs[attr_key]
                    if value == 'None':
                        data_dict[attr_key] = None
                    else:
                        data_dict[attr_key] = value
    
    # Reconstruct the class
    class_name = class_data.pop('__class__')
    module_name = class_data.pop('__module__')
    
    # Import the module and get the class
    module = __import__(module_name, fromlist=[class_name])
    cls = getattr(module, class_name)
    
    # Create instance
    instance = cls(**class_data)
    
    return instance, data_dict


def get_init_params(obj):
    """Returns a list of parameters entering `__init__` of `obj`."""
    if hasattr(obj, '__init__'):
        sig = inspect.signature(obj.__init__)
        params = list(sig.parameters.keys())
        # Remove 'self' parameter
        if params and params[0] == 'self':
            params = params[1:]
        return params
    return []