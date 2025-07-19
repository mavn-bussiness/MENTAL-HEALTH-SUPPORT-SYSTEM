from django import forms
from .models import Assessment, Question, LikertOption, AssessmentResponse, ResponseAnswer

class AssessmentResponseForm(forms.ModelForm):
    class Meta:
        model = AssessmentResponse
        fields = []
    
    def __init__(self, *args, **kwargs):
        self.assessment = kwargs.pop('assessment')
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        for question in self.assessment.questions.all().order_by('order'):
            if question.question_type == 'likert':
                options = question.options.all().order_by('order')
                choices = [(opt.value, opt.text) for opt in options]
                self.fields[f'question_{question.id}'] = forms.ChoiceField(
                    label=question.text,
                    choices=choices,
                    widget=forms.RadioSelect(),
                    required=True
                )

    def save(self, commit=True):
        response = super().save(commit=False)
        response.assessment = self.assessment
        response.user = self.user
        
        # Calculate total score
        total_score = 0
        for question in self.assessment.questions.all():
            answer = self.cleaned_data.get(f'question_{question.id}')
            if answer:
                total_score += int(answer) * question.weight
        
        response.score = total_score
        response.risk_level = self.determine_risk_level(total_score)
        
        if commit:
            response.save()
            self.save_answers(response)
        
        return response
    
    def determine_risk_level(self, score):
        """Determine risk level based on assessment type and score"""
        assessment_type = self.assessment.assessment_type
        
        if assessment_type == 'phq9':  # PHQ-9 scoring
            if score <= 4: return 'none'
            elif 5 <= score <= 9: return 'mild'
            elif 10 <= score <= 14: return 'moderate'
            elif 15 <= score <= 19: return 'moderately_severe'
            else: return 'severe'
        elif assessment_type == 'gad7':  # GAD-7 scoring
            if score <= 4: return 'none'
            elif 5 <= score <= 9: return 'mild'
            elif 10 <= score <= 14: return 'moderate'
            else: return 'severe'
        # Add other assessment types as needed
        return 'none'
    
    def save_answers(self, response):
        for question in self.assessment.questions.all():
            answer_value = self.cleaned_data.get(f'question_{question.id}')
            if answer_value is not None:
                ResponseAnswer.objects.create(
                    response=response,
                    question=question,
                    answer_value=answer_value
                )