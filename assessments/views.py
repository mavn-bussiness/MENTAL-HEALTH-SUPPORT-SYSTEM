from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AssessmentForm, AssessmentResult
from .forms import DynamicAssessmentForm

def get_risk_level_and_recommendations(form_type, total_score):
    # Placeholder for risk level and recommendations logic
    # Should return (risk_level, recommendations)
    return 'low', 'Keep up the good work!'

@login_required
def assessment_list(request):
    """List available assessments"""
    if request.user.role != 'client':
        messages.error(request, 'Access denied.')
        return redirect('accounts:landing')
    
    forms = AssessmentForm.objects.filter(is_active=True)
    user_results = AssessmentResult.objects.filter(user=request.user)
    completed_forms = set(result.form.id for result in user_results)
    
    context = {
        'forms': forms,
        'completed_forms': completed_forms,
    }
    
    return render(request, 'assessments/assessment_list.html', context)

@login_required
def take_assessment(request, form_id):
    """Take an assessment"""
    if request.user.role != 'client':
        messages.error(request, 'Access denied.')
        return redirect('accounts:landing')
    
    assessment_form = get_object_or_404(AssessmentForm, id=form_id, is_active=True)
    
    # Check if user has already completed this assessment
    existing_result = AssessmentResult.objects.filter(
        user=request.user,
        form=assessment_form
    ).first()
    
    if existing_result:
        messages.info(request, 'You have already completed this assessment.')
        return redirect('assessments:assessment_results', result_id=existing_result.id)
    
    if request.method == 'POST':
        form = DynamicAssessmentForm(assessment_form, request.POST)
        if form.is_valid():
            total_score, responses = form.calculate_score()
            
            # Determine risk level and recommendations
            risk_level, recommendations = get_risk_level_and_recommendations(
                assessment_form.form_type, total_score
            )
            
            # Save assessment result
            result = AssessmentResult.objects.create(
                user=request.user,
                form=assessment_form,
                responses=responses,
                total_score=total_score,
                risk_level=risk_level,
                recommendations=recommendations
            )
            
            messages.success(request, 'Assessment completed successfully!')
            return redirect('assessments:assessment_results', result_id=result.id)
    else:
        form = DynamicAssessmentForm(assessment_form)
    
    context = {
        'form': form,
        'assessment_form': assessment_form,
    }
    
    return render(request, 'assessments/take_assessment.html', context)

@login_required
def assessment_results(request, result_id):
    result = get_object_or_404(AssessmentResult, id=result_id, user=request.user)
    return render(request, 'assessments/assessment_results.html', {'result': result})
