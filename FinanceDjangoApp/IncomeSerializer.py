# from rest_framework import serializers
# from .models import Income, Source, Activity
# from datetime import date


# class IncomeSerializer(serializers.Serializer):
#     payerDetail = serializers.CharField(max_length=100)
#     remarks = serializers.CharField(required=False, allow_blank=True)
#     amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
#     sourceName = serializers.CharField(max_length=45)

from rest_framework import serializers

class IncomeSerializer(serializers.Serializer):
    payerDetail = serializers.CharField(max_length=100)
    remarks = serializers.CharField(required=False, allow_blank=True)  # Optional field
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    sourceName = serializers.CharField(max_length=45)  # For mapping to sourceID in the backend
