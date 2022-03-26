from rest_framework import serializers
from person.models import Person


class PersonSerializers(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'
    level_id = serializers.StringRelatedField()
