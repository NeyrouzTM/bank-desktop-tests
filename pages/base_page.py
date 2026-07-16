import os
import subprocess
import sys
import time
from pathlib import Path

from pywinauto import Desktop


class BaseTkPage:

    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[1]
        self.pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
        self.desktop = Desktop(backend="win32")
        self.process = None
        self.window = None

    def _wait_for_window(self, title, timeout=10):
        deadline = time.time() + timeout

        while time.time() < deadline:
            windows = self.desktop.windows(title=title)
            if windows:
                return windows[-1]
            time.sleep(0.2)

        raise RuntimeError(f"{title} window not found")

    def _attach_window(self, title, timeout=10):
        # Wait until window exists, then focus.
        self.window = self._wait_for_window(title, timeout=timeout)
        try:
            self.window.set_focus()
        except Exception:
            pass

        # Tk widgets are sometimes created right after focus; wait briefly
        # but don't assume they are ready immediately.
        for _ in range(10):
            try:
                # Trigger handle refresh
                _ = self.window.children()
                break
            except Exception:
                time.sleep(0.1)
        time.sleep(0.2)
        return self.window


    def _launch_script(self, script_path):
        existing_handles = {
            window.handle for window in self.desktop.windows(title=self.window_title)
        }

        self.process = subprocess.Popen(
            [self.pythonw, str(self.project_root / script_path)],
            cwd=str(self.project_root),
        )

        self.window = self._wait_for_new_window(self.window_title, existing_handles)
        return self.window

    def _launch_code(self, code):
        existing_handles = {
            window.handle for window in self.desktop.windows(title=self.window_title)
        }

        self.process = subprocess.Popen(
            [self.pythonw, "-c", code],
            cwd=str(self.project_root),
        )

        self.window = self._wait_for_new_window(self.window_title, existing_handles)
        return self.window

    def _wait_for_new_window(self, title, existing_handles, timeout=10):
        deadline = time.time() + timeout

        while time.time() < deadline:
            candidates = [
                window
                for window in self.desktop.windows(title=title)
                if window.handle not in existing_handles
            ]
            if candidates:
                return candidates[0]
            time.sleep(0.2)

        raise RuntimeError(f"{title} window not found")

    def _unique_controls(self):
        found = []
        seen = set()
        stack = list(self.window.children())
        while stack:
            control = stack.pop(0)
            handle = getattr(control, "handle", None)
            if handle in seen:
                continue
            if handle is not None:
                seen.add(handle)
            found.append(control)
            try:
                stack.extend(list(control.children()))
            except Exception:
                pass
        return found

    def _entry_controls(self):
        # Prefer direct children first (placed automation controls)
        direct_controls = self._entry_candidates(list(self.window.children()))
        if direct_controls:
            return direct_controls

        return self._entry_candidates(self._unique_controls())

    def _entry_candidates(self, pool):
        controls = []
        seen = set()
        for child in pool:
            handle = getattr(child, "handle", None)
            if handle in seen:
                continue
            try:
                if child.class_name() != "TkChild":
                    continue
                rect = child.rectangle()
                height = rect.bottom - rect.top
                width = rect.right - rect.left
            except Exception:
                continue
            if 18 <= height <= 42 and 150 <= width <= 420:
                seen.add(handle)
                controls.append(child)

        controls = self._discard_entry_containers(controls)
        controls = self._dedupe_by_rectangle(controls)
        controls.sort(key=lambda control: (control.rectangle().top, control.rectangle().left))
        return controls

    def _dedupe_by_rectangle(self, controls):
        filtered = []
        seen = set()
        for control in controls:
            rect = control.rectangle()
            key = (rect.left, rect.top, rect.right, rect.bottom)
            if key in seen:
                continue
            seen.add(key)
            filtered.append(control)
        return filtered

    def _discard_entry_containers(self, controls):
        filtered = []
        rectangles = [(control, control.rectangle()) for control in controls]

        for control, rect in rectangles:
            is_container = False
            rect_width = rect.right - rect.left
            rect_height = rect.bottom - rect.top
            rect_area = rect_width * rect_height

            for other, other_rect in rectangles:
                if other is control:
                    continue

                other_width = other_rect.right - other_rect.left
                other_height = other_rect.bottom - other_rect.top
                other_area = other_width * other_height
                overlap_width = max(
                    0,
                    min(rect.right, other_rect.right) - max(rect.left, other_rect.left),
                )
                overlap_height = max(
                    0,
                    min(rect.bottom, other_rect.bottom) - max(rect.top, other_rect.top),
                )
                overlap_area = overlap_width * overlap_height

                if rect_area > other_area and overlap_area >= other_area * 0.5:
                    is_container = True
                    break

            if not is_container:
                filtered.append(control)

        return filtered

    def _buttons(self):
        buttons = []
        seen = set()
        for child in self._unique_controls():
            handle = getattr(child, "handle", None)
            if handle in seen:
                continue
            try:
                if child.class_name() != "Button":
                    continue
            except Exception:
                continue
            seen.add(handle)
            buttons.append(child)
        buttons.sort(key=lambda control: (control.rectangle().top, control.rectangle().left))
        return buttons

    def _button_by_text(self, text):
        wanted = text.strip().lower()
        exact_matches = []
        partial_matches = []
        for child in self._buttons():
            try:
                label = (child.window_text() or "").strip().lower()
            except Exception:
                label = ""
            if label == wanted:
                exact_matches.append(child)
            elif label and wanted in label:
                partial_matches.append(child)
        if exact_matches:
            return exact_matches[0]
        if partial_matches:
            return partial_matches[0]

        if wanted == "login":
            buttons = self._buttons()
            if buttons:
                # Login screen has a single primary button
                return buttons[0]

        raise RuntimeError(f"Button '{text}' not found")

    def _click_and_type(self, control, value):
        # Tk controls can be present but not yet visible/actionable right after redraw.
        last_exc = None
        for _ in range(15):
            try:
                control.click_input()
                time.sleep(0.1)
                break
            except Exception as e:
                last_exc = e
                time.sleep(0.15)

        if last_exc is not None:
            # One last attempt will raise if still not actionable.
            pass

        # Clear current content (if supported) then type.
        try:
            control.type_keys("^a{BACKSPACE}", with_spaces=True)
        except Exception:
            # Fallback: try plain backspace if Ctrl+A is not supported
            try:
                control.type_keys("{BACKSPACE}", with_spaces=True)
            except Exception:
                pass

        if value:
            last_exc = None
            for _ in range(10):
                try:
                    control.type_keys(value, with_spaces=True)
                    last_exc = None
                    break
                except Exception as e:
                    last_exc = e
                    time.sleep(0.15)

            if last_exc is not None:
                raise last_exc

        time.sleep(0.05)

