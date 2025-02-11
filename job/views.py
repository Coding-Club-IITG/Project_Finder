from difflib import context_diff
from django.shortcuts import render,redirect
from django.contrib import messages
from .models import Job,ApplyJob
from .forms import CreateJobForm,UpdateJobForm
from users.models import User 
from company.models import Company
from notifications.models import Notif
from resume.models import Resume


def create_job(request):
    if request.user.is_recruiter and request.user.has_company: 
        if request.method == 'POST':
            form =  CreateJobForm(request.POST)
            if form.is_valid():
                var = form.save(commit=False)
                var.user = request.user
                var.company = request.user.company
                var.save()
                applicants = Resume.objects.filter(title = var.title)
                for applicant in applicants:
                    user = applicant.user
                    Notif.objects.create(
                        user = user,
                        content = f'There is a new job opening for the role of {var.title} offered by {var.company}'
                    )
                messages.info(request, 'New job has been created')
                return redirect('dashboard')
            else:
                messages.warning(request, 'Something went wrong')
                return redirect('create-job')
        else:
            form = CreateJobForm()
            context = {'form':form}
            return render(request, 'job/create_job.html', context)
    else:
        messages.warning(request, 'Permission Denied')
        return redirect('dashboard')


def update_job(request, pk):
    job = Job.objects.get(pk=pk)
    if request.method == 'POST':
        form = UpdateJobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            applicants = Resume.objects.filter(title = job.title)
            for applicant in applicants:
                user = applicant.user
                Notif.objects.create(
                    user = user,
                    content = f'There has been an update in the job offer for the role of {job.title} offered by {job.company}'
                )
            messages.info(request, 'Your job info is updated')
            return redirect('dashboard')
        else:
            messages.warning(request, 'Something went wrong')
    else:
        form = UpdateJobForm(instance=job)
        context = {'form':form}
        return render(request, 'job/update_job.html', context)


def manage_jobs(request):
    jobs = Job.objects.filter(user=request.user, company=request.user.company)
    context = {'jobs':jobs}
    return render(request, 'job/manage_jobs.html', context)

def apply_to_job(request, pk):
    if request.user.is_authenticated and request.user.is_applicant:    #user must be of applicant type to apply
        job = Job.objects.get(pk = pk)

        if ApplyJob.objects.filter(user = request.user, job = pk).exists():  #if user has already applied
            messages.warning(request, 'Permission Denied')
            return redirect('dashboard') 
        else:                           
            ApplyJob.objects.create(                            
                job = job,
                user = request.user,
                status = 'Pending'
            )
            applicant = Resume.objects.get(user=request.user)
            applicant = f'{applicant.first_name} {applicant.surname}'
            Notif.objects.create(
                user = job.company.user,
                content = f'{applicant} has applied to your company {job.company} for the role of {job.title}'
            )
            messages.info(request, 'You have successfully applied! Please see dashboard')
            return redirect('dashboard')
    else:
        messages.info(request, 'Please log in to continue')
        return redirect('login')

        
def all_applicants(request, pk):
    job = Job.objects.get(pk=pk)
    applicants = job.applyjob_set.all()
    context = {'job':job, 'applicants':applicants}
    return render(request, 'job/all_applicants.html', context)

def applied_jobs(request):
    jobs = ApplyJob.objects.filter(user=request.user)
    context = {'jobs':jobs}
    return render(request, 'job/applied_job.html', context)
    