import json

from django.views.generic import View, ListView, DetailView
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from truegrit.models import (
    BusinessUnit,
    Camera,
    TimeEntry,
    Project,
    ServerRole, 
    CameraModel,
    InstallationStatus,
    InstallationMountType,
    Network,
    DistributionFrameRole,
    ProjectStatus,
    VideoQualityResolution,
)    

class Timekeeper(View):

    template_name = 'timekeeper.html'
    context = {}

    def get(self, request, *args, **kwargs):
        self.context["greeting"] = "hello"
        return render(request, self.template_name, self.context)

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add another context variable
        # all_cameras = Camera.objects.all()
        # total_cameras = all_cameras.count()
        # completed_cameras = all_cameras.filter(mac_address__isnull=True).count()
        to_do = 0
        for unit in BusinessUnit.objects.all():
            if not unit.is_completed():
                to_do += Camera.objects.filter(network__business_unit=unit).count()
        print(to_do)
        return context


class BusinessUnitDetailView(DetailView):
    model = BusinessUnit
    template_name = 'businessunit_detail.html'
    context_object_name = 'business_unit'

    def get_object(self, queryset=None):
        uuid_ = self.kwargs.get('uuid')
        return get_object_or_404(BusinessUnit, uuid=uuid_)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(self.request.GET.get('sort'))
        print("---")
        # Retrieve the sort parameter and order direction from the GET request
        sort_by = self.request.GET.get('sort', 'ip_address')  # Default to sorting by ip_address
        # order = self.request.GET.get('order', 'asc')  # Default order is ascending
        print(sort_by)
        # # Determine the sort order
        # if order == 'asc':
        #     sort_order = sort_by  # Sort in ascending order
        # else:
        #     sort_order = f'-{sort_by}'  # Sort in descending order
        if "-" in sort_by:
            order = "dsc"
        else:
            order = "asc"

        context['sort_by'] = sort_by
        context['order'] = order  # Store the current order in context
        context['cameras'] = Camera.objects.filter(
            network__business_unit=context['business_unit']).order_by(sort_by)
        return context
    
def create_time_entry(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            start_time = data.get('start_time')
            raw_project_number = data.get('project_number')
            project_description = data.get('task_description')

          
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        
        project_number_string = ''.join([char for char in raw_project_number if char.isdigit()])
        project_number = int(project_number_string)
        
        try:
            project = Project.objects.get(
                number=project_number
            ) 
        except ObjectDoesNotExist:
            print("create new project")
            new_project = Project(
                number = project_number,
                status = ProjectStatus.objects.get(name="current")
            )
            new_project.set_fields_to_base()
            new_project.save()
            project = new_project
        print("new project: {}".format(project))
        # Create and save the new TimeEntry instance
        new_entry = TimeEntry.objects.create(
            start_time=start_time,
            project=project,
            project_description=project_description
        )

        # Return success response
        return JsonResponse({"message": "Time entry created successfully", "id": new_entry.id})

    return JsonResponse({"error": "Invalid request method"}, status=405)    