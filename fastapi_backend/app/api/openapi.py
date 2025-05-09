from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.core.config import settings


def custom_openapi(app: FastAPI):
    """
    Tùy chỉnh schema OpenAPI
    """
    def openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=settings.PROJECT_NAME,
            version=settings.VERSION,
            description=settings.DESCRIPTION,
            routes=app.routes,
        )

        # Add JWT Bearer security scheme
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter JWT Bearer token",
            }
        }

        # Custom authentication information
        openapi_schema["info"] = {
            "title": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "description": settings.DESCRIPTION,
            "contact": {
                "name": "EduScan API Support",
                "email": "support@eduscan.vn",
            },
            "license": {
                "name": "MIT",
                "url": "https://opensource.org/licenses/MIT",
            },
        }

        # Add global security scheme
        openapi_schema["security"] = [{"BearerAuth": []}]

        # Add custom response examples
        for path in openapi_schema.get("paths", {}).values():
            for method in path.values():
                if "responses" in method:
                    for status, response in method["responses"].items():
                        if status == "401":
                            response["content"] = {
                                "application/json": {
                                    "example": {
                                        "success": False,
                                        "message": "Không được phép truy cập",
                                        "error_code": "HTTP_401",
                                    }
                                }
                            }
                        elif status == "403":
                            response["content"] = {
                                "application/json": {
                                    "example": {
                                        "success": False,
                                        "message": "Không đủ quyền truy cập",
                                        "error_code": "HTTP_403",
                                    }
                                }
                            }
                        elif status == "422":
                            response["content"] = {
                                "application/json": {
                                    "example": {
                                        "success": False,
                                        "message": "Lỗi xác thực dữ liệu",
                                        "error_code": "VALIDATION_ERROR",
                                        "details": {
                                            "field": "Lỗi xác thực"
                                        }
                                    }
                                }
                            }

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return openapi 