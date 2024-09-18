from django.views.generic import View, ListView
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from truegrit.models import (
    BusinessUnit,
    Camera,
    ServerRole, 
    CameraModel,
    InstallationStatus,
    InstallationMountType,
    DistributionFrameRole,
    ProjectStatus,
    VideoQualityResolution,
)    


class FrontPage(View):

    template_name = 'index.html'
    context = {}

    def get(self, request, *args, **kwargs):
        self.context["cameras"] = Camera.objects.all()
        # self.context["users"] = User.objects.all()
        # self.context["server_roles"] = ServerRole.objects.all()
        # self.context["camera_models"] = CameraModel.objects.all()
        # self.context["installation_mounttypes"] = InstallationMountType.objects.all()
        # self.context["installation_status"] = InstallationStatus.objects.all()
        # self.context["distributionframeroles"] = DistributionFrameRole.objects.all()
        # self.context["project_status"] = ProjectStatus.objects.all()
        # self.context["resolutions"] = VideoQualityResolution.objects.all()
        return render(request, self.template_name, self.context)
    
class BusinessUnitListView(ListView):
    model = BusinessUnit
    template_name = 'business_units.html'  
    context_object_name = 'units'       

