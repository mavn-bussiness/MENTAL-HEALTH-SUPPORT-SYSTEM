from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Assessment, AssessmentResponse, Recommendation
from .forms import AssessmentResponseForm

def assessment_list(request):
    assessments = Assessment.objects.filter(is_active=True)
    completed_ids = []
    
    if request.user.is_authenticated:
        completed_ids = list(
            AssessmentResponse.objects.filter(user=request.user)
            .values_list('assessment_id', flat=True)
        )
    
    return render(request, 'assessments/assessment_list.html', {
        'assessments': assessments,
        'completed_forms': completed_ids
    })

@login_required
def take_assessment(request, assessment_id):
    assessment = get_object_or_404(Assessment, pk=assessment_id, is_active=True)
    
    # Prefetch questions and options for performance
    assessment = Assessment.objects.prefetch_related(
        'questions',
        'questions__options'
    ).get(pk=assessment.id)
    
    if request.method == 'POST':
        form = AssessmentResponseForm(request.POST, assessment=assessment, user=request.user)
        if form.is_valid():
            response = form.save()
            return redirect('assessments:assessment_results', response_id=response.id)
    else:
        form = AssessmentResponseForm(assessment=assessment, user=request.user)
    
    return render(request, 'assessments/take_assessment.html', {
        'assessment': assessment,
        'form': form
    })

@login_required
def assessment_results(request, response_id):
    response = get_object_or_404(AssessmentResponse, pk=response_id, user=request.user)
    recommendation = Recommendation.objects.filter(
        assessment=response.assessment,
        min_score__lte=response.score,
        max_score__gte=response.score
    ).first()
    
    return render(request, 'assessments/assessment_results.html', {
        'result': response,
        'recommendation': recommendation
    })

@login_required
def user_results(request):
    responses = AssessmentResponse.objects.filter(user=request.user).order_by('-completed_at')
    return render(request, 'assessments/assessment_results.html', {
        'responses': responses
    })