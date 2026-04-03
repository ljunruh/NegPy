import unittest
from unittest.mock import MagicMock

from negpy.desktop.controller import AppController
from negpy.desktop.session import DesktopSessionManager, AppState
from negpy.services.rendering.preview_manager import PreviewManager

class TestAppController(unittest.TestCase):
    def setUp(self):
        # Create a mock session manager
        self.mock_session_manager = MagicMock(spec=DesktopSessionManager)
        self.mock_session_manager.state = AppState()
        self.mock_session_manager.repo = MagicMock()
        
        # We need a QCoreApplication instance to create QThreads inside AppController
        import sys
        from PyQt6.QtCore import QCoreApplication
        if not QCoreApplication.instance():
            self.app = QCoreApplication(sys.argv)
        else:
            self.app = QCoreApplication.instance()
            
        self.controller = AppController(self.mock_session_manager)
        
        # Mock preview service
        self.controller.preview_service = MagicMock(spec=PreviewManager)
        self.controller.preview_service.load_linear_preview.return_value = (None, (0, 0), {})

    def tearDown(self):
        # Clean up dynamically created threads
        for thread in [
            self.controller.render_thread,
            self.controller.export_thread,
            self.controller.thumb_thread,
            self.controller.norm_thread,
            self.controller.discovery_thread
        ]:
            if thread is not None and thread.isRunning():
                thread.quit()
                thread.wait()

    def test_load_file_emits_zoom_reset(self):
        """Test that loading a file normally resets the zoom."""
        mock_slot = MagicMock()
        self.controller.zoom_requested.connect(mock_slot)
        
        self.controller.load_file("dummy.dng")
        
        mock_slot.assert_called_once_with(1.0)
        self.assertFalse(self.controller.state.hq_preview)
        
    def test_load_file_preserve_zoom(self):
        """Test that load_file with preserve_zoom=True skips resetting zoom."""
        mock_slot = MagicMock()
        self.controller.zoom_requested.connect(mock_slot)
        
        self.controller.load_file("dummy.dng", preserve_zoom=True)
        
        mock_slot.assert_not_called()
        
    def test_toggle_hq_preview_preserves_zoom(self):
        """Test that toggling HQ mode automatically preserves zoom."""
        self.controller.state.current_file_path = "dummy.dng"
        
        mock_slot = MagicMock()
        self.controller.zoom_requested.connect(mock_slot)
        
        self.controller.toggle_hq_preview()
        
        # State should be toggled
        self.assertTrue(self.controller.state.hq_preview)
        
        # Zoom should NOT be reset
        mock_slot.assert_not_called()


if __name__ == "__main__":
    unittest.main()
