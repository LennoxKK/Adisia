from django.shortcuts import render
from rest_framework.views import APIView
from accounts.models import *
from .serializers import *
from rest_framework.response import Response

class ReactView(APIView):
    def get(self,request):
        output = [{
            "username":output.username,
            "phone":output.phone,}
                  for output in User.objects.all()]
        return Response(output)
    def post(self,request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        