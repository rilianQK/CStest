from typing import Dict, List, Any
from enum import Enum

from .models import ChromePermission, RiskLevel
from .extension import Extension


# Risk score mapping for each risk level
risk_score_map = {
    RiskLevel.NONE: 0,
    RiskLevel.LOW: 10,
    RiskLevel.MEDIUM: 30,
    RiskLevel.HIGH: 60,
    RiskLevel.CRITICAL: 100
}

# Permission to risk level mapping
permissions_risk_map = {
    # NONE risk permissions
    ChromePermission.ALARMS: RiskLevel.NONE,
    ChromePermission.FONT_SETTINGS: RiskLevel.NONE,
    ChromePermission.IDLE: RiskLevel.NONE,
    ChromePermission.NOTIFICATIONS: RiskLevel.NONE,
    ChromePermission.POWER: RiskLevel.NONE,
    ChromePermission.RUNTIME: RiskLevel.NONE,
    ChromePermission.STORAGE: RiskLevel.NONE,
    ChromePermission.TTS: RiskLevel.NONE,
    ChromePermission.TTS_ENGINE: RiskLevel.NONE,
    ChromePermission.WALLPAPER: RiskLevel.NONE,
    
    # LOW risk permissions
    ChromePermission.ACTIVE_TAB: RiskLevel.LOW,
    ChromePermission.BACKGROUND: RiskLevel.LOW,
    ChromePermission.CONTEXT_MENUS: RiskLevel.LOW,
    ChromePermission.DECLARATIVE_CONTENT: RiskLevel.LOW,
    ChromePermission.DESKTOP_CAPTURE: RiskLevel.LOW,
    ChromePermission.GCM: RiskLevel.LOW,
    ChromePermission.OFFSCREEN: RiskLevel.LOW,
    ChromePermission.PAGE_CAPTURE: RiskLevel.LOW,
    ChromePermission.SCRIPTING: RiskLevel.LOW,
    ChromePermission.SIDE_PANEL: RiskLevel.LOW,
    ChromePermission.TAB_GROUPS: RiskLevel.LOW,
    ChromePermission.TOP_SITES: RiskLevel.LOW,
    
    # MEDIUM risk permissions
    ChromePermission.BOOKMARKS: RiskLevel.MEDIUM,
    ChromePermission.DOWNLOADS: RiskLevel.MEDIUM,
    ChromePermission.DOWNLOADS_OPEN: RiskLevel.MEDIUM,
    ChromePermission.DOWNLOADS_UI: RiskLevel.MEDIUM,
    ChromePermission.FAVICON: RiskLevel.MEDIUM,
    ChromePermission.GEOLOCATION: RiskLevel.MEDIUM,
    ChromePermission.MANAGEMENT: RiskLevel.MEDIUM,
    ChromePermission.PRINTING: RiskLevel.MEDIUM,
    ChromePermission.PRINTING_METRICS: RiskLevel.MEDIUM,
    ChromePermission.READING_LIST: RiskLevel.MEDIUM,
    ChromePermission.SEARCH: RiskLevel.MEDIUM,
    ChromePermission.SESSIONS: RiskLevel.MEDIUM,
    ChromePermission.TABS: RiskLevel.MEDIUM,
    ChromePermission.UNLIMITED_STORAGE: RiskLevel.MEDIUM,
    
    # HIGH risk permissions
    ChromePermission.ACCESSIBILITY_FEATURES_MODIFY: RiskLevel.HIGH,
    ChromePermission.ACCESSIBILITY_FEATURES_READ: RiskLevel.HIGH,
    ChromePermission.AUDIO: RiskLevel.HIGH,
    ChromePermission.BROWSING_DATA: RiskLevel.HIGH,
    ChromePermission.CLIPBOARD_READ: RiskLevel.HIGH,
    ChromePermission.CLIPBOARD_WRITE: RiskLevel.HIGH,
    ChromePermission.CONTENT_SETTINGS: RiskLevel.HIGH,
    ChromePermission.DEBUGGER: RiskLevel.HIGH,
    ChromePermission.DECLARATIVE_NET_REQUEST: RiskLevel.HIGH,
    ChromePermission.DECLARATIVE_NET_REQUEST_FEEDBACK: RiskLevel.HIGH,
    ChromePermission.DECLARATIVE_NET_REQUEST_WITH_HOST_ACCESS: RiskLevel.HIGH,
    ChromePermission.DECLARATIVE_WEB_REQUEST: RiskLevel.HIGH,
    ChromePermission.DISPLAY_SOURCE: RiskLevel.HIGH,
    ChromePermission.DNS: RiskLevel.HIGH,
    ChromePermission.DOCUMENT_SCAN: RiskLevel.HIGH,
    ChromePermission.ENTERPRISE_DEVICE_ATTRIBUTES: RiskLevel.HIGH,
    ChromePermission.ENTERPRISE_HARDWARE_PLATFORM: RiskLevel.HIGH,
    ChromePermission.ENTERPRISE_NETWORKING_ATTRIBUTES: RiskLevel.HIGH,
    ChromePermission.ENTERPRISE_PLATFORM_KEYS: RiskLevel.HIGH,
    ChromePermission.EXPERIMENTAL: RiskLevel.HIGH,
    ChromePermission.FILE_BROWSER_HANDLER: RiskLevel.HIGH,
    ChromePermission.FILE_SYSTEM_PROVIDER: RiskLevel.HIGH,
    ChromePermission.HISTORY: RiskLevel.HIGH,
    ChromePermission.IDENTITY: RiskLevel.HIGH,
    ChromePermission.IDENTITY_EMAIL: RiskLevel.HIGH,
    ChromePermission.LOGIN_STATE: RiskLevel.HIGH,
    ChromePermission.NATIVE_MESSAGING: RiskLevel.HIGH,
    ChromePermission.PLATFORM_KEYS: RiskLevel.HIGH,
    ChromePermission.PRINTER_PROVIDER: RiskLevel.HIGH,
    ChromePermission.PRIVACY: RiskLevel.HIGH,
    ChromePermission.PROCESSES: RiskLevel.HIGH,
    ChromePermission.PROXY: RiskLevel.HIGH,
    ChromePermission.SYSTEM_CPU: RiskLevel.HIGH,
    ChromePermission.SYSTEM_DISPLAY: RiskLevel.HIGH,
    ChromePermission.SYSTEM_MEMORY: RiskLevel.HIGH,
    ChromePermission.SYSTEM_STORAGE: RiskLevel.HIGH,
    ChromePermission.TAB_CAPTURE: RiskLevel.HIGH,
    ChromePermission.VPN_PROVIDER: RiskLevel.HIGH,
    ChromePermission.WEB_AUTHENTICATION_PROXY: RiskLevel.HIGH,
    ChromePermission.WEB_NAVIGATION: RiskLevel.HIGH,
    ChromePermission.WEB_REQUEST: RiskLevel.HIGH,
    ChromePermission.WEB_REQUEST_BLOCKING: RiskLevel.HIGH,
    
    # CRITICAL risk permissions
    ChromePermission.CERTIFICATE_PROVIDER: RiskLevel.CRITICAL,
    ChromePermission.COOKIES: RiskLevel.CRITICAL,
    ChromePermission.INPUT_COMPONENTS: RiskLevel.CRITICAL,
    ChromePermission.OAUTH2: RiskLevel.CRITICAL,
}


def get_risk_level(permission) -> RiskLevel:
    """
    Determine the risk level associated with a given Chrome permission or permission string.
    
    Args:
        permission: Permission string or ChromePermission enum
        
    Returns:
        RiskLevel enum value
    """
    # Handle string permissions
    if isinstance(permission, str):
        # Try to convert string to ChromePermission enum
        try:
            permission_enum = ChromePermission(permission)
            return permissions_risk_map.get(permission_enum, RiskLevel.MEDIUM)
        except ValueError:
            # Check if it's a host permission (starts with http:// or https://)
            if permission.startswith(('http://', 'https://')):
                return RiskLevel.HIGH
            # Check for wildcard patterns
            elif '*' in permission:
                return RiskLevel.HIGH
            # Default to MEDIUM for unknown string permissions
            return RiskLevel.MEDIUM
    
    # Handle ChromePermission enum
    elif isinstance(permission, ChromePermission):
        return permissions_risk_map.get(permission, RiskLevel.MEDIUM)
    
    # Default fallback
    return RiskLevel.MEDIUM


def get_risk_score(risk_level: RiskLevel) -> int:
    """
    Map a risk level to its corresponding numerical risk score.
    
    Args:
        risk_level: RiskLevel enum value
        
    Returns:
        Numerical risk score (0-100)
    """
    return risk_score_map.get(risk_level, 30)


def get_risk_report(extension: Extension) -> Dict[str, Any]:
    """
    Generate a risk report for a given browser extension.
    
    Args:
        extension: Extension object to analyze
        
    Returns:
        Dictionary containing risk assessment report
    """
    # Analyze permissions and calculate risk scores
    permission_risks = []
    total_risk_score = 0
    permission_count = 0
    
    for permission in extension.permissions:
        risk_level = get_risk_level(permission)
        risk_score = get_risk_score(risk_level)
        
        permission_risks.append({
            'permission': permission,
            'risk_level': risk_level.value,
            'risk_score': risk_score
        })
        
        total_risk_score += risk_score
        permission_count += 1
    
    # Calculate overall risk score (average of permission risks, capped at 100)
    overall_risk_score = min(100, total_risk_score // max(1, permission_count)) if permission_count > 0 else 0
    
    # Build the risk report
    report = {
        'name': extension.name,
        'version': extension.version,
        'author': extension.author,
        'browser': extension.browser.value,
        'extension_id': extension.extension_id,
        'manifest_version': extension.manifest_version,
        'sha256': extension.sha256,
        'homepage_url': extension.homepage_url,
        'risk_score': overall_risk_score,
        'permissions': permission_risks,
        'javascript_files': extension.javascript_files,
        'urls': extension.urls
    }
    
    return report