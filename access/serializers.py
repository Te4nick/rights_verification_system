from rest_framework import serializers


class CheckAccessSerializer(serializers.Serializer):
    user = serializers.CharField(min_length=3, max_length=20, required=True)
    resource = serializers.CharField(min_length=3, required=True)


class AccessSerializer(serializers.Serializer):
    read = serializers.BooleanField(default=False)
    write = serializers.BooleanField(default=False)
    execute = serializers.BooleanField(default=False)


class ModifyAccessSerializer(CheckAccessSerializer, AccessSerializer):
    pass


class ForbiddenAccessSerializer(serializers.Serializer):
    forbidden = serializers.DictField(
        child=serializers.ListField(
            child=serializers.CharField()
        )
    )


class ValidationErrorSerializer(serializers.Serializer):
    errors = serializers.DictField(
        child=serializers.ListField(
            child=serializers.CharField()
        )
    )
