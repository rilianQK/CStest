from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, HttpUrl


class RiskLevel(str, Enum):
    """Define an enumeration of risk levels with string values representing different severity categories."""
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ChromePermission(str, Enum):
    """Enumerate and categorize Chrome extension API permissions for controlling access to browser features and system resources."""
    ACCESSIBILITY_FEATURES_MODIFY = "accessibilityFeatures.modify"
    ACCESSIBILITY_FEATURES_READ = "accessibilityFeatures.read"
    ACTIVE_TAB = "activeTab"
    ALARMS = "alarms"
    AUDIO = "audio"
    BACKGROUND = "background"
    BOOKMARKS = "bookmarks"
    BROWSING_DATA = "browsingData"
    CERTIFICATE_PROVIDER = "certificateProvider"
    CLIPBOARD_READ = "clipboardRead"
    CLIPBOARD_WRITE = "clipboardWrite"
    CONTENT_SETTINGS = "contentSettings"
    CONTEXT_MENUS = "contextMenus"
    COOKIES = "cookies"
    DEBUGGER = "debugger"
    DECLARATIVE_CONTENT = "declarativeContent"
    DECLARATIVE_NET_REQUEST = "declarativeNetRequest"
    DECLARATIVE_NET_REQUEST_FEEDBACK = "declarativeNetRequestFeedback"
    DECLARATIVE_NET_REQUEST_WITH_HOST_ACCESS = "declarativeNetRequestWithHostAccess"
    DECLARATIVE_WEB_REQUEST = "declarativeWebRequest"
    DESKTOP_CAPTURE = "desktopCapture"
    DISPLAY_SOURCE = "displaySource"
    DNS = "dns"
    DOCUMENT_SCAN = "documentScan"
    DOWNLOADS = "downloads"
    DOWNLOADS_OPEN = "downloads.open"
    DOWNLOADS_UI = "downloads.ui"
    ENTERPRISE_DEVICE_ATTRIBUTES = "enterprise.deviceAttributes"
    ENTERPRISE_HARDWARE_PLATFORM = "enterprise.hardwarePlatform"
    ENTERPRISE_NETWORKING_ATTRIBUTES = "enterprise.networkingAttributes"
    ENTERPRISE_PLATFORM_KEYS = "enterprise.platformKeys"
    EXPERIMENTAL = "experimental"
    FAVICON = "favicon"
    FILE_BROWSER_HANDLER = "fileBrowserHandler"
    FILE_SYSTEM_PROVIDER = "fileSystemProvider"
    FONT_SETTINGS = "fontSettings"
    GCM = "gcm"
    GEOLOCATION = "geolocation"
    HISTORY = "history"
    IDENTITY = "identity"
    IDENTITY_EMAIL = "identity.email"
    IDLE = "idle"
    LOGIN_STATE = "loginState"
    MANAGEMENT = "management"
    NATIVE_MESSAGING = "nativeMessaging"
    NOTIFICATIONS = "notifications"
    OFFSCREEN = "offscreen"
    PAGE_CAPTURE = "pageCapture"
    PLATFORM_KEYS = "platformKeys"
    POWER = "power"
    PRINTER_PROVIDER = "printerProvider"
    PRINTING = "printing"
    PRINTING_METRICS = "printingMetrics"
    PRIVACY = "privacy"
    PROCESSES = "processes"
    PROXY = "proxy"
    READING_LIST = "readingList"
    RUNTIME = "runtime"
    SCRIPTING = "scripting"
    SEARCH = "search"
    SESSIONS = "sessions"
    SIDE_PANEL = "sidePanel"
    STORAGE = "storage"
    SYSTEM_CPU = "system.cpu"
    SYSTEM_DISPLAY = "system.display"
    SYSTEM_MEMORY = "system.memory"
    SYSTEM_STORAGE = "system.storage"
    TABS = "tabs"
    TAB_CAPTURE = "tabCapture"
    TAB_GROUPS = "tabGroups"
    TOP_SITES = "topSites"
    TTS = "tts"
    TTS_ENGINE = "ttsEngine"
    UNLIMITED_STORAGE = "unlimitedStorage"
    VPN_PROVIDER = "vpnProvider"
    WALLPAPER = "wallpaper"
    WEB_AUTHENTICATION_PROXY = "webAuthenticationProxy"
    WEB_NAVIGATION = "webNavigation"
    WEB_REQUEST = "webRequest"
    WEB_REQUEST_BLOCKING = "webRequestBlocking"


class BackgroundConfig(BaseModel):
    """Define the configuration settings for background processes, including service worker paths, persistence flags, and script lists."""
    persistent: bool
    scripts: Optional[List[str]] = None
    service_worker: Optional[str] = None


class CrossOriginPolicy(BaseModel):
    """Define a data model for representing Cross-Origin Resource Sharing (CORS) policies with a string value."""
    value: str


class ExternallyConnectable(BaseModel):
    """Define a model for specifying external connection capabilities, including matching patterns, identifiers, and TLS channel acceptance."""
    matches: Optional[List[str]] = None
    ids: Optional[List[str]] = None
    accepts_tls_channel_id: Optional[bool] = None


class FileSystemProviderCapabilities(BaseModel):
    """Define the capabilities of a filesystem provider, including configurability, support for multiple mounts, and source type."""
    configurable: bool
    multiple_mounts: bool
    source: str


class ImportConfig(BaseModel):
    """Define a Pydantic model for validating import configuration data with a required 32-character alphanumeric ID field."""
    id: str


class IncognitoMode(str, Enum):
    """Define the modes of incognito operation as an enumeration for configuration or state management."""
    NOT_ALLOWED = "not_allowed"
    SPANNING = "spanning"
    SPLIT = "split"


class OmniboxConfig(BaseModel):
    """Define a configuration model for an omnibox feature, specifying a keyword parameter as a required string field."""
    keyword: str


class OptionsUI(BaseModel):
    """The OptionsUI class defines a configuration model for UI options, specifying whether to use a Chrome-like style and the target page to display."""
    chrome_style: bool
    page: str


class SidePanel(BaseModel):
    """Represents a side panel configuration with an optional default path setting."""
    default_path: Optional[str] = None


class Storage(BaseModel):
    """Define a data model for storage configuration with a managed schema attribute."""
    managed_schema: str


class ChromeManifest(BaseModel):
    """Define a structured model for Chrome extension manifest files with required, recommended, and optional fields."""
    manifest_version: int
    name: str
    version: str
    
    action: Optional[Dict[str, Any]] = None
    author: Optional[str] = None
    automation: Optional[Any] = None
    background: Optional[BackgroundConfig] = None
    chrome_settings_overrides: Optional[Dict[str, Any]] = None
    chrome_url_overrides: Optional[Dict[str, Any]] = None
    commands: Optional[Dict[str, Any]] = None
    content_capabilities: Optional[Any] = None
    content_scripts: Optional[List[Dict[str, Any]]] = None
    content_security_policy: Optional[Union[Dict[str, str], str]] = None
    converted_from_user_script: Optional[Any] = None
    cross_origin_embedder_policy: Optional[CrossOriginPolicy] = None
    cross_origin_opener_policy: Optional[CrossOriginPolicy] = None
    current_locale: Optional[str] = None
    declarative_net_request: Optional[Any] = None
    default_locale: Optional[str] = None
    description: Optional[str] = None
    devtools_page: Optional[str] = None
    differential_fingerprint: Optional[Any] = None
    event_rules: Optional[List[Dict[str, Any]]] = None
    externally_connectable: Optional[ExternallyConnectable] = None
    file_browser_handlers: Optional[List[Any]] = None
    file_system_provider_capabilities: Optional[FileSystemProviderCapabilities] = None
    homepage_url: Optional[str] = None
    host_permissions: Optional[List[str]] = None
    icons: Optional[Dict[str, str]] = None
    import_: Optional[List[ImportConfig]] = None
    incognito: Optional[IncognitoMode] = None
    input_components: Optional[Any] = None
    key: Optional[str] = None
    minimum_chrome_version: Optional[str] = None
    nacl_modules: Optional[List[Any]] = None
    natively_connectable: Optional[Any] = None
    oauth2: Optional[Any] = None
    offline_enabled: Optional[bool] = None
    omnibox: Optional[OmniboxConfig] = None
    optional_host_permissions: Optional[List[str]] = None
    optional_permissions: Optional[List[Union[ChromePermission, str]]] = None
    options_page: Optional[str] = None
    options_ui: Optional[OptionsUI] = None
    permissions: Optional[List[Union[ChromePermission, str]]] = None
    platforms: Optional[Any] = None
    replacement_web_app: Optional[Any] = None
    requirements: Optional[Dict[str, Any]] = None
    sandbox: Optional[Dict[Any, Any]] = None
    short_name: Optional[str] = None
    side_panel: Optional[SidePanel] = None
    storage: Optional[Storage] = None
    system_indicator: Optional[Any] = None
    tts_engine: Optional[Dict[str, Any]] = None
    update_url: Optional[HttpUrl] = None
    version_name: Optional[str] = None
    web_accessible_resources: Optional[List[Union[Dict[str, Any], str]]] = None