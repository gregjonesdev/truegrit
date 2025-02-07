import json

from datetime import date, timedelta, datetime
from django.views.generic import View, ListView, DetailView
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from uuid import UUID

from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from truegrit.models import (
    BusinessUnit,
    Camera,
    SubTask,
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
        recent_projects = []
        for entry in TimeEntry.objects.all().order_by('-created_at'):
            if len(recent_projects) < 5 and not entry.project in recent_projects:
                recent_projects.append(entry.project)
        self.context["recent_projects"] = recent_projects
        return render(request, self.template_name, self.context)

def project_detail(request, uuid):
    project = get_object_or_404(Project, uuid=uuid)
    date = request.GET.get('date')
    entries = []
    for each in project.timeentry_set.all():
        if each.get_duration() > 0 and str(each.start_time.date()) == date:
            entries.append(each)
    print(entries)        
    return render(request, 'project.html', {'entries': entries})     

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


class Daily(View):

    template_name = 'dailytime.html'
    context = {}

    def get(self, request, *args, **kwargs):
        # date.today()
        target_date = request.GET.get('date', None)
    
        if target_date:
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        else:
            target_date = datetime.today().date()
        print(target_date)
        self.context["friendly_date"] = target_date.strftime("%A, %m/%d")
        # projects = []
        # for project in Project.objects.all():
        #     time_entries = project.timeentry_set.filter(start_time__date=target_date)
        #     if len(time_entries) > 0:
        #         print(project.uuid)
        #         projects.append({
        #             "project": project,
        #             "date": request.GET.get('date', None),
        #             "time_entries": time_entries,
        #             "daily_hours": project.get_daily_hours(target_date)
        #         })
        #     project.get_daily_hours(target_date)
        self.context["daily_time_entries"] = TimeEntry.objects.filter(start_time__date=target_date)  
        return render(request, self.template_name, self.context)

class Weekly(View):

    template_name = 'weeklytime.html'
    context = {}

    def get(self, request, *args, **kwargs):
        target_date = date.today()
        # Calculate the number of days since Monday (0 = Monday, 1 = Tuesday, ..., 6 = Sunday)
        days_since_monday = target_date.weekday()
        # Subtract the days since Monday from today to get the date of this week's Monday
        monday_date = target_date - timedelta(days=days_since_monday)
        projects = []
        daily_totals = [0, 0, 0, 0, 0, 0, 0]
        for project in Project.objects.all():
            day_offset = 0
            hours = []
            while day_offset < 7:
                daily_hours = project.get_daily_hours(monday_date + timedelta(days=day_offset))
                hours.append(daily_hours)
                daily_totals[day_offset] += daily_hours
                
                day_offset += 1
            total_hours = sum(hours)
            if total_hours > 0:
                projects.append({
                    "project": project,
                    "hours": hours,
                    "total_hours": total_hours
                })      
        self.context["daily_totals"] = daily_totals
        self.context["weekly_total"] = sum(daily_totals)
        self.context["projects"] = projects 
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

def edit_time_entry(request, id):
    print("192")
    try:
        # Convert the 'id' from the URL to a UUID object
        time_entry_uuid = UUID(id)
    except ValueError:
        # If the UUID is invalid, raise a 404 error
        raise Http404("Invalid time entry ID.")

    try:
        # Fetch the TimeEntry object using the UUID
        time_entry = TimeEntry.objects.get(uuid=time_entry_uuid)
    except TimeEntry.DoesNotExist:
        # If no object is found with that UUID, raise a 404 error
        raise Http404("Time entry not found.")
    
    # Render the modal content with the time entry object
    if request.method == 'POST':
        print("hell post")
        time_entry_date = time_entry.start_time.date()
        print(time_entry.start_time)
        time_start = request.POST.get('time_start')  # Extract the time_start parameter
        if time_start:
            start_time_str = f"{time_entry_date} {time_start}"
            time_entry.start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M")
        time_end = request.POST.get('time_end')
        if time_end and time_end > time_start:
            end_time_str = f"{time_entry_date} {time_end}"
            time_entry.end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M")
        time_entry.save()
        return JsonResponse({
                "entry_uuid": time_entry.uuid,
                "start_time": time_start, 
                "end_time": time_end, 
            })
    else:
        return render(request, 'edittimemodal.html', {'time_entry': time_entry})

    
def create_time_entry(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            start_time = data.get('start_time')
            project_number = data.get('project_number').upper().replace("PJT","")
            project_description = data.get('project_description')

          
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
        
        if project_number:
            try:
                project = Project.objects.get(
                    number=project_number
                ) 
            except ObjectDoesNotExist:
                new_project = Project(
                    number = project_number,
                    status = ProjectStatus.objects.get(name="current")
                )
                new_project.set_fields_to_base()
                new_project.save()
                project = new_project    
            project.description = project_description
            project.save()
        else:    
            try:
                project = Project.objects.get(
                    description=project_description
                ) 
            except ObjectDoesNotExist:
                print("create new 159")
                new_project = Project(
                    description = project_description,
                    status = ProjectStatus.objects.get(name="current")
                )
                new_project.set_fields_to_base()
                new_project.save()
                project = new_project    

        
        # Create and save the new TimeEntry instance
        new_entry = TimeEntry(
            start_time=start_time,
            project=project,
        )
        new_entry.set_fields_to_base()
        new_entry.save()

        # Return success response
        return JsonResponse({
            "message": "Time entry created successfully", 
            "projectNumber": new_entry.project.get_prefixed_number(),
            "startTime": new_entry.start_time.split(" ")[-1],
            "projectDescription": new_entry.project.description,
            "timeEntryUuid": new_entry.uuid
            })

    return JsonResponse({"error": "Invalid request method"}, status=405)  

def save_task(request):
    if request.method == 'POST':
        print("hiyeah")
        try:
            data = json.loads(request.body)  
            print("data:")
            print(data)

            timeEntry = TimeEntry.objects.get(uuid=data.get("timeEntryUuid"))
            task_description = data.get("task_description")
            new_task = SubTask(
                time_entry=timeEntry,
                description=task_description
            )
            new_task.set_fields_to_base()
            new_task.save()
            print("------")
            for task in SubTask.objects.filter(time_entry=timeEntry):
                print(task.description)
            return JsonResponse({
                "message": "Time entry created successfully", 
                "timeCreated": new_task.created_at,
                "taskDescription": task_description
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)       


def complete_time_entry(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            complete_time = data.get('finish_time') 
            timeEntryUuid = data.get('timeEntryUuid') 

            timeEntry = TimeEntry.objects.get(uuid=timeEntryUuid)
            print(timeEntry)
            timeEntry.end_time = complete_time
            timeEntry.save()
            print(timeEntry)
            return JsonResponse({
                "message": "Time entry completed successfully", 
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
