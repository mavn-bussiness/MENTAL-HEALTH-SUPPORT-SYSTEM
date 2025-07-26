from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Avg
from .models import Assessment, AssessmentResponse, Recommendation
from .forms import AssessmentResponseForm

@login_required
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
        'questions__options'
    ).get(pk=assessment_id)

    questions = list(assessment.questions.all())
    # Check if assessment has no questions
    if not questions:
        messages.error(request, 'This assessment is not available because it has no questions. Please contact the administrator.')
        return render(request, 'assessments/take_assessment.html', {
            'assessment': assessment,
            'form': None
        })
    # Check if any likert/multiple question has no options
    for question in questions:
        if question.question_type in ['likert', 'multiple'] and question.options.count() == 0:
            messages.error(request, f'The question "{question.text}" has no options configured. Please contact the administrator.')
            return render(request, 'assessments/take_assessment.html', {
                'assessment': assessment,
                'form': None
            })
    
    if request.method == 'POST':
        form = AssessmentResponseForm(request.POST, assessment=assessment, user=request.user)
        if form.is_valid():
            response = form.save()
            return redirect('assessments:assessment_results', response_id=response.id)
        else:
            messages.error(request, 'Please correct the errors in the form.')
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
    responses = AssessmentResponse.objects.filter(user=request.user).select_related('assessment').order_by('-completed_at')
    return render(request, 'assessments/user_results.html', {
        'responses': responses
    })

@staff_member_required
@login_required
def assessment_analytics(request):
    """Admin view for assessment completion and score analytics"""
    total_completed = AssessmentResponse.objects.count()
    completions_by_type = AssessmentResponse.objects.values('assessment__assessment_type').annotate(
        count=Count('id'),
        avg_score=Avg('score')
    )
    high_risk_responses = AssessmentResponse.objects.filter(
        is_flagged=True
    ) | AssessmentResponse.objects.filter(risk_level__in=['moderately_severe', 'severe'])
    
    context = {
        'total_completed': total_completed,
        'completions_by_type': completions_by_type,
        'high_risk_responses': high_risk_responses,
    }
    return render(request, 'assessments/assessment_analytics.html', context)