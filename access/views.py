from uuid import UUID

from django.shortcuts import render
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .models import AccessLogStatus
from .services.access_service import AccessService
from .services.log_service import LogService
from .serializers import (
    ModifyAccessSerializer,
    ValidationErrorSerializer,
    CheckAccessSerializer,
    AccessSerializer,
    ForbiddenAccessSerializer,
    OperationSerializer,
    GetOperationQuerySerializer,
)
from .services.ops_service import OperationsService


@extend_schema_view(
    post_access=extend_schema(
        summary="Post new user access to resource",
        request=ModifyAccessSerializer,
        responses={
            status.HTTP_201_CREATED: ModifyAccessSerializer,
            status.HTTP_422_UNPROCESSABLE_ENTITY: ValidationErrorSerializer,
        },
        auth=False,
    ),
    get_access=extend_schema(
        summary="User access rights to resource",
        parameters=[CheckAccessSerializer],
        responses={
            status.HTTP_200_OK: AccessSerializer,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
            status.HTTP_422_UNPROCESSABLE_ENTITY: ValidationErrorSerializer,
        },
        auth=False,
    ),
    get_forbidden=extend_schema(
        summary="Get forbidden accesses",
        responses={
            status.HTTP_200_OK: ForbiddenAccessSerializer,
        },
        auth=False,
    ),
    get_log_file=extend_schema(
        summary="Generate log.csv and get operation details",
        responses={
            status.HTTP_200_OK: OperationSerializer,
        },
        auth=False,
    ),
    get_log_file_status=extend_schema(
        summary="Get log generation status",
        parameters=[GetOperationQuerySerializer],
        responses={
            status.HTTP_200_OK: OperationSerializer,
            status.HTTP_404_NOT_FOUND: None,
            status.HTTP_422_UNPROCESSABLE_ENTITY: ValidationErrorSerializer,
        },
        auth=False,
    ),
)
class AccessViewSet(ViewSet):
    access_service = AccessService()
    log_service = LogService()
    ops_service = OperationsService()

    @action(detail=False, methods=["POST"])
    def post_access(self, request):
        in_access = ModifyAccessSerializer(data=request.data)
        if not in_access.is_valid():
            return Response(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                data=ValidationErrorSerializer({"errors": in_access.errors}).data,
            )

        self.access_service.add_entry(**in_access.data)
        return Response(
            status=status.HTTP_201_CREATED,
            data=ModifyAccessSerializer(in_access.data).data
        )

    @action(detail=False, methods=["GET"])
    def get_access(self, request):
        query_ser = CheckAccessSerializer(data=request.query_params)
        if not query_ser.is_valid():
            return Response(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                data=ValidationErrorSerializer({"errors": query_ser.errors}).data,
            )

        access = self.access_service.check_access(**query_ser.data)

        if access is AccessLogStatus.USER_NOT_FOUND:
            self.log_service.write_entry(**query_ser.data, status=access)
            return Response(
                status=status.HTTP_404_NOT_FOUND,
            )

        if access is AccessLogStatus.RESOURCE_NOT_FOUND:
            self.log_service.write_entry(**query_ser.data, status=access)
            return Response(
                status=status.HTTP_403_FORBIDDEN,
            )

        self.log_service.write_entry(**query_ser.data, status=AccessLogStatus.SUCCESS)
        return Response(
            status=status.HTTP_200_OK,
            data=AccessSerializer(access).data,
        )

    @action(detail=False, methods=["GET"])
    def get_forbidden(self, _):
        forbidden = self.access_service.get_forbidden_access()
        return Response(
            status=status.HTTP_200_OK,
            data=ForbiddenAccessSerializer({"forbidden": forbidden}).data,
        )

    @action(detail=False, methods=["GET"])
    def get_log_file(self, _):
        op_id = self.ops_service.execute_operation(self.log_service.get_log_file_path)
        op = self.ops_service.get_operation(op_id)
        return Response(
            status=status.HTTP_200_OK,
            data=OperationSerializer(op).data,
        )

    @action(detail=False, methods=["GET"])
    def get_log_file_status(self, request):
        query_ser = GetOperationQuerySerializer(data=request.query_params)
        if not query_ser.is_valid():
            return Response(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                data=ValidationErrorSerializer({"errors": query_ser.errors}).data,
            )

        op = self.ops_service.get_operation(UUID(query_ser.data.get("id")))
        if op is None:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            status=status.HTTP_200_OK,
            data=OperationSerializer(
                {
                    "id": op.id,
                    "done": op.done,
                    "result": {
                        "path": op.result,
                    },
                }
            ).data,
        )
