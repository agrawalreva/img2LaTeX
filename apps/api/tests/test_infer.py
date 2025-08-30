import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from ..app.main import app

client = TestClient(app)


def test_infer_success():
    """Test successful inference with valid image"""
    with patch('builtins.open', create=True), \
         patch('os.makedirs'), \
         patch('time.time', return_value=1234567890), \
         patch('time.sleep'):
        
        # Create mock image file
        mock_file = MagicMock()
        mock_file.content_type = "image/jpeg"
        mock_file.filename = "test.jpg"
        mock_file.read.return_value = b"fake_image_data"
        
        response = client.post(
            "/api/infer",
            files={"image": ("test.jpg", b"fake_image_data", "image/jpeg")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "latex" in data
        assert "tokens" in data
        assert "time_ms" in data
        assert "id" in data
        assert data["latex"] == "E = mc^2"


def test_infer_invalid_file():
    """Test inference with non-image file"""
    response = client.post(
        "/api/infer",
        files={"image": ("test.txt", b"not an image", "text/plain")}
    )
    
    assert response.status_code == 400
    assert "File must be an image" in response.json()["detail"]


def test_infer_no_file():
    """Test inference without file"""
    response = client.post("/api/infer")
    
    assert response.status_code == 422  # Validation error
