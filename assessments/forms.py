from django import forms
from .models import Assessment, AssessmentResponse, ResponseAnswer, Recommendation
from django.core.exceptions import ValidationError

class AssessmentResponseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.assessment = kwargs.pop('assessment')
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        for question in self.assessment.questions.all():
            field_name = f'question_{question.id}'
            if question.question_type == 'likert':
                choices = [(option.value, option.text) for option in question.options.all()]
                self.fields[field_name] = forms.ChoiceField(
                    choices=choices,
                    widget=forms.RadioSelect,
                    label=question.text,
                    required=True
                )
            elif question.question_type == 'multiple':
                choices = [(option.value, option.text) for option in question.options.all()]
                self.fields[field_name] = forms.ChoiceField(
                    choices=choices,
                    widget=forms.Select,
                    label=question.text,
                    required=True
                )
            else:  # text
                self.fields[field_name] = forms.CharField(
                    widget=forms.Textarea,
                    label=question.text,
                    required=False
                )

    def clean(self):
        cleaned_data = super().clean()
        total_score = 0
        for question in self.assessment.questions.all():
            field_name = f'question_{question.id}'
            if question.question_type in ['likert', 'multiple']:
                value = cleaned_data.get(field_name)
                if value is not None:
                    try:
                        total_score += int(value) * question.weight
                    except ValueError:
                        raise ValidationError(f"Invalid response for {question.text}")
        cleaned_data['total_score'] = total_score
        return cleaned_data

    def save(self):
        total_score = self.cleaned_data['total_score']
        recommendation = Recommendation.objects.filter(
            assessment=self.assessment,
            min_score__lte=total_score,
            max_score__gte=total_score
        ).first()
        
        risk_level = recommendation.risk_level if recommendation else 'none'
        is_flagged = risk_level in ['moderately_severe', 'severe']

        response = AssessmentResponse.objects.create(
            user=self.user,
            assessment=self.assessment,
            score=total_score,
            risk_level=risk_level,
            is_flagged=is_flagged
        )

        for question in self.assessment.questions.all():
            field_name = f'question_{question.id}'
            answer_value = self.cleaned_data.get(field_name)
            answer_text = answer_value if question.question_type == 'text' else None
            answer_value = int(answer_value) if question.question_type in ['likert', 'multiple'] else None
            
            ResponseAnswer.objects.create(
                response=response,
                question=question,
                answer_value=answer_value,
                answer_text=answer_text
            )

        return response