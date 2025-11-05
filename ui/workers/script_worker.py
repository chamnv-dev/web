# -*- coding: utf-8 -*-
"""
Script Worker - Non-blocking script generation using QThread
"""
from PyQt5.QtCore import QThread, pyqtSignal

# Constants for error message truncation
ERROR_DETAIL_MAX_LENGTH = 200
ERROR_GENERIC_MAX_LENGTH = 300


class ScriptWorker(QThread):
    """
    Background worker for script generation
    Prevents UI freezing during LLM API calls
    """
    
    # Signals
    progress = pyqtSignal(str)  # Progress messages
    done = pyqtSignal(dict)     # Result data
    error = pyqtSignal(str)     # Error messages
    
    def __init__(self, cfg: dict, parent=None):
        """
        Initialize script worker
        
        Args:
            cfg: Configuration dictionary with all settings
            parent: Parent QObject
        """
        super().__init__(parent)
        self.cfg = cfg
    
    def run(self):
        """Execute script generation in background thread"""
        try:
            self.progress.emit("Đang tạo kịch bản...")
            
            from services.sales_script_service import build_outline
            
            result = build_outline(self.cfg)
            
            self.progress.emit("Hoàn thành!")
            self.done.emit(result)
            
        except Exception as e:
            # Provide user-friendly error messages
            error_type = type(e).__name__
            error_str = str(e)
            
            # Format error message based on type
            if error_type == "JSONDecodeError":
                user_msg = (
                    "❌ Lỗi phân tích phản hồi từ AI\n\n"
                    "AI trả về dữ liệu không hợp lệ. Có thể do:\n"
                    "• Nội dung quá dài (giảm xuống < 5000 ký tự)\n"
                    "• Ký tự đặc biệt không hợp lệ\n"
                    "• Lỗi tạm thời từ AI\n\n"
                    f"Chi tiết: {error_str[:ERROR_DETAIL_MAX_LENGTH]}"
                )
            elif error_type == "MissingAPIKey":
                user_msg = (
                    "❌ Thiếu API Key\n\n"
                    "Vui lòng cấu hình Google API Key trong tab Cài đặt."
                )
            elif "timeout" in error_str.lower() or "timed out" in error_str.lower():
                user_msg = (
                    "❌ Hết thời gian chờ\n\n"
                    "Kết nối đến AI mất quá nhiều thời gian.\n"
                    "Vui lòng kiểm tra kết nối mạng và thử lại."
                )
            else:
                user_msg = f"❌ Lỗi: {error_type}\n\n{error_str[:ERROR_GENERIC_MAX_LENGTH]}"
            
            self.error.emit(user_msg)
