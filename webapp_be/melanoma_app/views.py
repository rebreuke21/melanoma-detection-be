from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.models import Group
from django.utils import timezone
from django.http import HttpResponse, FileResponse
from .models import User, Image, Image_Classification, Region
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import StaticHTMLRenderer, JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, GroupSerializer, CustomUserSerializer, ImageSerializer
from .image_processing import process_image
import base64

from PIL import Image as pilImage

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class CustomUserCreate(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format='json'):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetLesions(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, region):

        response_data = '{"results": ['
        count_l = 0

        lesions = Image.objects.filter(patient=request.user, region=Region.objects.get(region=region)).values("lesion_id", "description").distinct()

        for l in lesions:
            response_data += '{"lesion_id":"' + str(l['lesion_id']) +'","description":"' + l['description'] +'"}'
            count_l += 1
            if (count_l < len(lesions)):
                response_data += ','
        
        response_data += "]}"
        return HttpResponse(response_data, status=status.HTTP_200_OK)


class UploadImage(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        image = Image()
        image.patient = request.user
        image.image = request.data['image']
        image.name = str(request.data['image'])
        image.date_uploaded = timezone.now()
        image.region = Region.objects.get(region=request.data['region'])
        image.directory = "media"
        image.lesion_id = request.data['lesion_id']
        image.description = request.data['description']
        image.image_classification = Image_Classification.objects.get(classification='unclear')
        image.save()
        ic = process_image(image)
        image.image_classification = Image_Classification.objects.get(classification=ic)
        image.save()
        response_message = '{"classification":"' + image.image_classification.classification + '"}'
        return HttpResponse(response_message, status=status.HTTP_200_OK)

class UploadImageAutoID(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        image = Image()
        image.patient = request.user
        image.image = request.data['image']
        image.name = str(request.data['image'])
        image.date_uploaded = timezone.now()
        image.region = Region.objects.get(region=request.data['region'])
        image.directory = "media"

        if (request.data['newLesion'] == "true"):
            lesions = Image.objects.filter(patient=request.user, region=Region.objects.get(region=request.data['region'])).values("lesion_id").distinct()
            image.lesion_id = len(lesions) + 1
            image.description = request.data['description']
        else:
            lesions = Image.objects.filter(patient=request.user, region=Region.objects.get(region=request.data['region']), lesion_id=request.data['lesion_id']).values("description").distinct()
            image.lesion_id = request.data['lesion_id']
            image.description = lesions[0]['description']
        image.image_classification = Image_Classification.objects.get(classification='unclear')
        image.save()
        ic = process_image(image)
        image.image_classification = Image_Classification.objects.get(classification=ic)
        image.save()
        response_message = '{"classification":"' + image.image_classification.classification + '"}'
        return HttpResponse(response_message, status=status.HTTP_200_OK)

class GetImages(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        images = Image.objects.filter(patient=request.user).order_by('-pk')
        response_data = '{"results": ['
        count = 0
        for i in images:
            """image_serializer = ImageSerializer(i, context={"request":request}).data
            print(image_serializer)
            response_data += str(image_serializer)
            count+=1
            if (count < len(images)):
                response_data += ","""

            image_classification = i.image_classification.classification
            name = i.name
            region = i.region.region
            lesion_id = str(i.lesion_id)
            description = str(i.description)
            date_uploaded = str(i.date_uploaded)
            """image_url = settings.MEDIA_ROOT + "/" + str(i.image)
            with open(image_url, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')"""
            #response_data += '{"image":"' + image_data + '", "image_classification":"'
            response_data += '{'
            """response_data += '"image":"data:image/jpg;base64, ' + image_data + '"'
            response_data += ','"""
            response_data += '"name":"' + name + '"'
            response_data += ','
            response_data += '"image_classification":"' + image_classification + '"'
            response_data += ','
            response_data += '"region":"' + region + '"'
            response_data += ','
            response_data += '"lesion_id":"' + lesion_id + '"'
            response_data += ','
            response_data += '"description":"' + description + '"'
            response_data += ','
            response_data += '"date_uploaded":"' + date_uploaded + '"'
            response_data += '}'
            count+=1
            if (count < len(images)):
                response_data += ','
        response_data += "]}"
        return HttpResponse(response_data, status=status.HTTP_200_OK)

class GetImagesByRegion(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        count_r = 0
        response_data = '{"results": ['
        regions = Region.objects.filter()

        for r in regions:
            count_l = 0
            response_data += '{"region":"' + r.region +'","lesions":['

            lesions = Image.objects.filter(patient=request.user, region=r.pk).values("lesion_id", "description").distinct()

            for l in lesions:
                count_i = 0
                response_data += '{"lesion_id":"' + str(l['lesion_id']) +'","description":"' + l['description'] +'","images":['
                images = Image.objects.filter(patient=request.user, region=r.pk, lesion_id=l['lesion_id']).values('name','image_classification','date_uploaded').order_by('-pk')
                for i in images:
                    name = i['name']
                    image_classification = Image_Classification.objects.get(pk=i['image_classification']).classification
                    date_uploaded = str(i['date_uploaded'])
                    response_data += '{'
                    response_data += '"name":"' + name + '"'
                    response_data += ','
                    response_data += '"image_classification":"' + image_classification + '"'
                    response_data += ','
                    response_data += '"date_uploaded":"' + date_uploaded + '"'
                    response_data += '}'
                    count_i += 1
                    if (count_i < len(images)):
                        response_data += ','
            
                response_data += "]}"
                count_l += 1
                if (count_l < len(lesions)):
                    response_data += ','
            
            response_data += "]}"
            count_r += 1
            if (count_r < len(regions)):
                response_data += ','
        response_data += "]}"
        return HttpResponse(response_data, status=status.HTTP_200_OK)

class GetImage(APIView):
    def get(self, request, imagename):
        image_url = settings.MEDIA_ROOT + "/images/" + imagename

        img = open(image_url, 'rb')
        return FileResponse(img)
        """with open(image_url, "rb") as image_file:
            #image_data = image_file.read()
            image_data = image_file.read()
            return HttpResponse(image_data, content_type="image/jpeg", status=status.HTTP_200_OK)
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
        return Response(image_data)"""


"""r = Region(region='head')
        r.save()
        r2 = Region(region='front_torso')
        r2.save()
        r3 = Region(region='back_torso')
        r3.save()
        r4 = Region(region='right_arm')
        r4.save()
        r5 = Region(region='left_arm')
        r5.save()
        r6 = Region(region='right_leg')
        r6.save()
        r7 = Region(region='left_leg')
        r7.save()

        c = Image_Classification(classification="unclear")
        c.save()
        c2 = Image_Classification(classification="nevus")
        c2.save()
        c3 = Image_Classification(classification="benign")
        c3.save()
        c4 = Image_Classification(classification="melanoma")
        c4.save()"""