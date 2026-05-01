"""
Safe keyboard and mouse input driver for game control.
Uses pynput for cross-platform input simulation with safety guards.

CRITICAL SAFETY FEATURES:
- Disabled by default (requires --enable-control flag)
- Global hotkey emergency stop (Ctrl+Alt+Esc)
- Action rate limiting
- Execution logging
- Session time limits
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import time
import threading

try:
    from pynput import keyboard, mouse
    from pynput.keyboard import Key, Controller as KeyboardController
    from pynput.mouse import Button, Controller as MouseController
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class SafeInputDriver:
    """
    Safe keyboard and mouse input driver with emergency stop.
    
    Safety features:
    - Global hotkey emergency stop (Ctrl+Alt+Esc)
    - Maximum actions per second rate limiting
    - Session timeout
    - Action logging
    - Explicit enable flag required
    """
    
    # Emergency stop hotkey combination
    EMERGENCY_HOTKEY = {Key.ctrl_l, Key.alt_l, Key.esc}
    
    def __init__(
        self,
        enabled: bool = False,
        max_actions_per_second: float = 10.0,
        max_session_duration_minutes: int = 60,
    ):
        """
        Initialize input driver.
        
        Args:
            enabled: Must be True to allow real input (safety feature)
            max_actions_per_second: Rate limit for actions
            max_session_duration_minutes: Maximum session duration
        """
        if not PYNPUT_AVAILABLE:
            raise ImportError(
                "pynput not installed. Install with: pip install pynput\n"
                "WARNING: Input control has safety implications. See docs/SAFETY.md"
            )
        
        self.enabled = enabled
        self.max_actions_per_second = max_actions_per_second
        self.min_action_interval = 1.0 / max_actions_per_second
        
        self.session_start = datetime.now()
        self.max_session_duration = timedelta(minutes=max_session_duration_minutes)
        
        self.emergency_stop = False
        self.last_action_time = 0.0
        self.action_count = 0
        
        # Controllers
        self.keyboard_ctrl = KeyboardController()
        self.mouse_ctrl = MouseController()
        
        # Action log
        self.action_log = []
        
        # Setup emergency stop listener
        self._setup_emergency_stop()
        
        if enabled:
            print("⚠️  INPUT CONTROL ENABLED ⚠️")
            print(f"Emergency stop: Press Ctrl+Alt+Esc")
            print(f"Max actions/second: {max_actions_per_second}")
            print(f"Session timeout: {max_session_duration_minutes} minutes")
        else:
            print("Input control DISABLED (safe mode)")
    
    def _setup_emergency_stop(self):
        """Setup global hotkey listener for emergency stop."""
        self.current_keys = set()
        
        def on_press(key):
            self.current_keys.add(key)
            if self.EMERGENCY_HOTKEY.issubset(self.current_keys):
                print("\n🛑 EMERGENCY STOP ACTIVATED 🛑")
                self.emergency_stop = True
        
        def on_release(key):
            if key in self.current_keys:
                self.current_keys.remove(key)
        
        # Start listener in background thread
        self.listener = keyboard.Listener(
            on_press=on_press,
            on_release=on_release
        )
        self.listener.start()
    
    def _check_safety(self) -> bool:
        """
        Check if it's safe to execute an action.
        
        Returns:
            bool: True if safe to proceed
        """
        # Check if enabled
        if not self.enabled:
            return False
        
        # Check emergency stop
        if self.emergency_stop:
            print("🛑 Action blocked: Emergency stop active")
            return False
        
        # Check session timeout
        if datetime.now() - self.session_start > self.max_session_duration:
            print("⏱️  Session timeout reached")
            self.emergency_stop = True
            return False
        
        # Check rate limiting
        current_time = time.time()
        if current_time - self.last_action_time < self.min_action_interval:
            time.sleep(self.min_action_interval - (current_time - self.last_action_time))
        
        self.last_action_time = time.time()
        return True
    
    def _log_action(self, action_type: str, action_data: Dict[str, Any]):
        """Log an action for debugging and safety audits."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "data": action_data,
        }
        self.action_log.append(log_entry)
        self.action_count += 1
    
    def press_key(self, key: str, duration: float = 0.1) -> bool:
        """
        Press and release a key.
        
        Args:
            key: Key to press (single character or Key constant name)
            duration: How long to hold the key (seconds)
            
        Returns:
            bool: True if action was executed
        """
        if not self._check_safety():
            return False
        
        try:
            # Convert string to Key if needed
            if len(key) == 1:
                key_obj = key
            else:
                key_obj = getattr(Key, key.lower(), None)
                if key_obj is None:
                    print(f"Unknown key: {key}")
                    return False
            
            # Press and hold
            self.keyboard_ctrl.press(key_obj)
            time.sleep(duration)
            self.keyboard_ctrl.release(key_obj)
            
            self._log_action("press_key", {"key": str(key), "duration": duration})
            return True
            
        except Exception as e:
            print(f"Error pressing key {key}: {e}")
            return False
    
    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """
        Type a string of text.
        
        Args:
            text: Text to type
            interval: Delay between keystrokes
            
        Returns:
            bool: True if action was executed
        """
        if not self._check_safety():
            return False
        
        try:
            for char in text:
                if self.emergency_stop:
                    break
                self.keyboard_ctrl.press(char)
                self.keyboard_ctrl.release(char)
                time.sleep(interval)
            
            self._log_action("type_text", {"text": text, "interval": interval})
            return True
            
        except Exception as e:
            print(f"Error typing text: {e}")
            return False
    
    def move_mouse(self, x: int, y: int, smooth: bool = False) -> bool:
        """
        Move mouse to absolute position.
        
        Args:
            x, y: Target coordinates
            smooth: Whether to move smoothly (slower but more natural)
            
        Returns:
            bool: True if action was executed
        """
        if not self._check_safety():
            return False
        
        try:
            if smooth:
                # Smooth movement
                current_x, current_y = self.mouse_ctrl.position
                steps = 10
                for i in range(steps + 1):
                    progress = i / steps
                    new_x = current_x + (x - current_x) * progress
                    new_y = current_y + (y - current_y) * progress
                    self.mouse_ctrl.position = (int(new_x), int(new_y))
                    time.sleep(0.01)
            else:
                self.mouse_ctrl.position = (x, y)
            
            self._log_action("move_mouse", {"x": x, "y": y, "smooth": smooth})
            return True
            
        except Exception as e:
            print(f"Error moving mouse: {e}")
            return False
    
    def click_mouse(self, button: str = "left", count: int = 1) -> bool:
        """
        Click mouse button.
        
        Args:
            button: "left", "right", or "middle"
            count: Number of clicks
            
        Returns:
            bool: True if action was executed
        """
        if not self._check_safety():
            return False
        
        try:
            button_obj = {
                "left": Button.left,
                "right": Button.right,
                "middle": Button.middle,
            }.get(button.lower(), Button.left)
            
            self.mouse_ctrl.click(button_obj, count)
            
            self._log_action("click_mouse", {"button": button, "count": count})
            return True
            
        except Exception as e:
            print(f"Error clicking mouse: {e}")
            return False
    
    def execute_action(self, action: str, params: Optional[Dict[str, Any]] = None) -> bool:
        """
        Execute a high-level game action.
        
        Args:
            action: Action name (e.g., "move_forward", "attack", "loot")
            params: Optional parameters
            
        Returns:
            bool: True if action was executed
        """
        params = params or {}
        
        # Map actions to key presses
        # This should be loaded from game-specific config in production
        action_mapping = {
            "move_forward": ("w", 0.5),
            "move_backward": ("s", 0.5),
            "turn_left": ("a", 0.3),
            "turn_right": ("d", 0.3),
            "attack": ("space", 0.1),
            "jump": ("space", 0.1),
            "interact": ("e", 0.1),
            "loot": ("f", 0.1),
            "use_item": ("1", 0.1),
            "open_inventory": ("i", 0.1),
        }
        
        if action not in action_mapping:
            print(f"Unknown action: {action}")
            return False
        
        key, duration = action_mapping[action]
        return self.press_key(key, duration)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get driver statistics."""
        elapsed = datetime.now() - self.session_start
        return {
            "enabled": self.enabled,
            "emergency_stop": self.emergency_stop,
            "session_duration_seconds": elapsed.total_seconds(),
            "max_session_seconds": self.max_session_duration.total_seconds(),
            "action_count": self.action_count,
            "actions_per_minute": self.action_count / (elapsed.total_seconds() / 60) if elapsed.total_seconds() > 0 else 0,
        }
    
    def stop(self):
        """Cleanup and stop the driver."""
        self.emergency_stop = True
        if hasattr(self, 'listener'):
            self.listener.stop()
        print("Input driver stopped")


class DryRunDriver:
    """Dry-run driver that only logs actions without executing."""
    
    def __init__(self):
        self.action_log = []
        print("🔒 Dry-run mode: Actions will be logged but not executed")
    
    def press_key(self, key: str, duration: float = 0.1) -> bool:
        log = f"[DRY-RUN] Press key: {key} for {duration}s"
        print(log)
        self.action_log.append(log)
        return True
    
    def type_text(self, text: str, interval: float = 0.05) -> bool:
        log = f"[DRY-RUN] Type: {text}"
        print(log)
        self.action_log.append(log)
        return True
    
    def move_mouse(self, x: int, y: int, smooth: bool = False) -> bool:
        log = f"[DRY-RUN] Move mouse to ({x}, {y})"
        print(log)
        self.action_log.append(log)
        return True
    
    def click_mouse(self, button: str = "left", count: int = 1) -> bool:
        log = f"[DRY-RUN] Click {button} button {count}x"
        print(log)
        self.action_log.append(log)
        return True
    
    def execute_action(self, action: str, params: Optional[Dict[str, Any]] = None) -> bool:
        log = f"[DRY-RUN] Execute action: {action}"
        print(log)
        self.action_log.append(log)
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        return {
            "enabled": False,
            "dry_run": True,
            "action_count": len(self.action_log),
        }
    
    def stop(self):
        print("Dry-run driver stopped")


def create_input_driver(
    enabled: bool = False,
    max_actions_per_second: float = 10.0,
    max_session_minutes: int = 60,
) -> SafeInputDriver:
    """
    Factory function to create input driver.
    
    Args:
        enabled: Whether to enable real input (requires explicit True)
        max_actions_per_second: Rate limit
        max_session_minutes: Session timeout
        
    Returns:
        SafeInputDriver or DryRunDriver
    """
    if not enabled:
        return DryRunDriver()
    
    if not PYNPUT_AVAILABLE:
        print("pynput not available, using DryRunDriver")
        return DryRunDriver()
    
    return SafeInputDriver(
        enabled=True,
        max_actions_per_second=max_actions_per_second,
        max_session_duration_minutes=max_session_minutes,
    )


if __name__ == "__main__":
    # Test driver in dry-run mode
    print("Input Driver Test (Dry-Run)")
    driver = create_input_driver(enabled=False)
    
    print("\nExecuting test actions...")
    driver.press_key("w")
    driver.execute_action("attack")
    driver.move_mouse(100, 200)
    driver.click_mouse("left")
    
    print("\nStatistics:")
    print(driver.get_statistics())
    
    driver.stop()
