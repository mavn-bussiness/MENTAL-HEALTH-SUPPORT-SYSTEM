"""
Django management command to populate assessment data
Save this as: management/commands/populate_assessments.py
Run with: python manage.py populate_assessments
"""

from django.core.management.base import BaseCommand
from assessments.models import Assessment, Question, LikertOption, Recommendation


class Command(BaseCommand):
    help = 'Populate database with standard mental health assessments'

    def handle(self, *args, **options):
        self.stdout.write('Creating mental health assessments...')
        
        # Create PHQ-9 Assessment
        self.create_phq9_assessment()
        
        # Create GAD-7 Assessment
        self.create_gad7_assessment()
        
        # Create PCL-5 Assessment
        self.create_pcl5_assessment()
        
        self.stdout.write(self.style.SUCCESS('Successfully created all assessments!'))

    def create_phq9_assessment(self):
        """Create PHQ-9 Depression Assessment"""
        
        # Create the assessment
        phq9, created = Assessment.objects.get_or_create(
            assessment_type='phq9',
            defaults={
                'title': 'PHQ-9 Depression Screening',
                'description': 'The Patient Health Questionnaire-9 (PHQ-9) is a validated tool for screening, diagnosing, monitoring and measuring the severity of depression.',
                'is_active': True,
                'version': '1.0',
                'min_score': 0,
                'max_score': 27
            }
        )
        
        if created:
            self.stdout.write(f'Created PHQ-9 assessment')
        
        # PHQ-9 Questions
        phq9_questions = [
            "Little interest or pleasure in doing things",
            "Feeling down, depressed, or hopeless",
            "Trouble falling or staying asleep, or sleeping too much",
            "Feeling tired or having little energy",
            "Poor appetite or overeating",
            "Feeling bad about yourself or that you are a failure or have let yourself or your family down",
            "Trouble concentrating on things, such as reading the newspaper or watching television",
            "Moving or speaking so slowly that other people could have noticed. Or the opposite being so fidgety or restless that you have been moving around a lot more than usual",
            "Thoughts that you would be better off dead, or of hurting yourself"
        ]
        
        # Create questions and options
        for i, question_text in enumerate(phq9_questions, 1):
            question, created = Question.objects.get_or_create(
                assessment=phq9,
                order=i,
                defaults={
                    'text': question_text,
                    'question_type': 'likert',
                    'weight': 1.0
                }
            )
            
            if created:
                # Create Likert options for each question
                likert_options = [
                    ("Not at all", 0),
                    ("Several days", 1),
                    ("More than half the days", 2),
                    ("Nearly every day", 3)
                ]
                
                for order, (option_text, value) in enumerate(likert_options, 1):
                    LikertOption.objects.get_or_create(
                        question=question,
                        order=order,
                        defaults={
                            'text': option_text,
                            'value': value
                        }
                    )
        
        # Create PHQ-9 Recommendations
        phq9_recommendations = [
            {
                'min_score': 0, 'max_score': 4, 'risk_level': 'none',
                'title': 'Minimal Depression',
                'description': 'Your responses suggest minimal or no depression symptoms.',
                'action_items': '• Continue healthy lifestyle habits\n• Practice stress management techniques\n• Maintain social connections\n• Consider regular mental health check-ins'
            },
            {
                'min_score': 5, 'max_score': 9, 'risk_level': 'mild',
                'title': 'Mild Depression',
                'description': 'Your responses suggest mild depression symptoms that may benefit from attention.',
                'action_items': '• Consider talking to a healthcare provider\n• Engage in regular physical activity\n• Practice mindfulness or meditation\n• Maintain regular sleep schedule\n• Connect with supportive friends or family'
            },
            {
                'min_score': 10, 'max_score': 14, 'risk_level': 'moderate',
                'title': 'Moderate Depression',
                'description': 'Your responses suggest moderate depression symptoms that warrant professional attention.',
                'action_items': '• Schedule an appointment with a healthcare provider\n• Consider counseling or therapy\n• Discuss treatment options with a professional\n• Maintain daily routines\n• Seek support from trusted individuals'
            },
            {
                'min_score': 15, 'max_score': 19, 'risk_level': 'moderately_severe',
                'title': 'Moderately Severe Depression',
                'description': 'Your responses suggest moderately severe depression that requires professional treatment.',
                'action_items': '• Seek immediate professional help\n• Consider medication evaluation\n• Engage in therapy or counseling\n• Inform trusted family members or friends\n• Create a safety plan if needed'
            },
            {
                'min_score': 20, 'max_score': 27, 'risk_level': 'severe',
                'title': 'Severe Depression',
                'description': 'Your responses suggest severe depression that requires immediate professional intervention.',
                'action_items': '• Seek immediate professional help\n• Consider emergency services if having thoughts of self-harm\n• Medication evaluation recommended\n• Intensive therapy or counseling\n• Ensure safety and support system activation'
            }
        ]
        
        for rec_data in phq9_recommendations:
            Recommendation.objects.get_or_create(
                assessment=phq9,
                min_score=rec_data['min_score'],
                max_score=rec_data['max_score'],
                defaults=rec_data
            )

    def create_gad7_assessment(self):
        """Create GAD-7 Anxiety Assessment"""
        
        # Create the assessment
        gad7, created = Assessment.objects.get_or_create(
            assessment_type='gad7',
            defaults={
                'title': 'GAD-7 Anxiety Screening',
                'description': 'The Generalized Anxiety Disorder-7 (GAD-7) is a validated screening tool for anxiety disorders and measuring anxiety severity.',
                'is_active': True,
                'version': '1.0',
                'min_score': 0,
                'max_score': 21
            }
        )
        
        if created:
            self.stdout.write(f'Created GAD-7 assessment')
        
        # GAD-7 Questions
        gad7_questions = [
            "Feeling nervous, anxious, or on edge",
            "Not being able to stop or control worrying",
            "Worrying too much about different things",
            "Trouble relaxing",
            "Being so restless that it's hard to sit still",
            "Becoming easily annoyed or irritable",
            "Feeling afraid as if something awful might happen"
        ]
        
        # Create questions and options
        for i, question_text in enumerate(gad7_questions, 1):
            question, created = Question.objects.get_or_create(
                assessment=gad7,
                order=i,
                defaults={
                    'text': question_text,
                    'question_type': 'likert',
                    'weight': 1.0
                }
            )
            
            if created:
                # Create Likert options for each question
                likert_options = [
                    ("Not at all", 0),
                    ("Several days", 1),
                    ("More than half the days", 2),
                    ("Nearly every day", 3)
                ]
                
                for order, (option_text, value) in enumerate(likert_options, 1):
                    LikertOption.objects.get_or_create(
                        question=question,
                        order=order,
                        defaults={
                            'text': option_text,
                            'value': value
                        }
                    )
        
        # Create GAD-7 Recommendations
        gad7_recommendations = [
            {
                'min_score': 0, 'max_score': 4, 'risk_level': 'none',
                'title': 'Minimal Anxiety',
                'description': 'Your responses suggest minimal or no anxiety symptoms.',
                'action_items': '• Continue healthy lifestyle habits\n• Practice relaxation techniques\n• Maintain regular exercise routine\n• Consider mindfulness practices'
            },
            {
                'min_score': 5, 'max_score': 9, 'risk_level': 'mild',
                'title': 'Mild Anxiety',
                'description': 'Your responses suggest mild anxiety symptoms that may benefit from self-care strategies.',
                'action_items': '• Practice deep breathing exercises\n• Try progressive muscle relaxation\n• Maintain regular sleep schedule\n• Limit caffeine intake\n• Consider speaking with a counselor'
            },
            {
                'min_score': 10, 'max_score': 14, 'risk_level': 'moderate',
                'title': 'Moderate Anxiety',
                'description': 'Your responses suggest moderate anxiety symptoms that warrant professional attention.',
                'action_items': '• Schedule appointment with healthcare provider\n• Consider therapy or counseling\n• Learn anxiety management techniques\n• Maintain support network\n• Practice regular self-care'
            },
            {
                'min_score': 15, 'max_score': 21, 'risk_level': 'severe',
                'title': 'Severe Anxiety',
                'description': 'Your responses suggest severe anxiety that requires professional treatment.',
                'action_items': '• Seek immediate professional help\n• Consider medication evaluation\n• Engage in therapy or counseling\n• Develop coping strategies with professional\n• Ensure strong support system'
            }
        ]
        
        for rec_data in gad7_recommendations:
            Recommendation.objects.get_or_create(
                assessment=gad7,
                min_score=rec_data['min_score'],
                max_score=rec_data['max_score'],
                defaults=rec_data
            )

    def create_pcl5_assessment(self):
        """Create PCL-5 PTSD Assessment"""
        
        # Create the assessment
        pcl5, created = Assessment.objects.get_or_create(
            assessment_type='pcl5',
            defaults={
                'title': 'PCL-5 PTSD Screening',
                'description': 'The PTSD Checklist for DSM-5 (PCL-5) is a validated assessment tool for screening and diagnosing PTSD.',
                'is_active': True,
                'version': '1.0',
                'min_score': 0,
                'max_score': 80
            }
        )
        
        if created:
            self.stdout.write(f'Created PCL-5 assessment')
        
        # PCL-5 Questions
        pcl5_questions = [
            "Repeated, disturbing, and unwanted memories of the stressful experience",
            "Repeated, disturbing dreams of the stressful experience",
            "Suddenly feeling or acting as if the stressful experience were actually happening again",
            "Feeling very upset when something reminded you of the stressful experience",
            "Having strong physical reactions when something reminded you of the stressful experience",
            "Avoiding memories, thoughts, or feelings related to the stressful experience",
            "Avoiding external reminders of the stressful experience",
            "Trouble remembering important parts of the stressful experience",
            "Having strong negative beliefs about yourself, other people, or the world",
            "Blaming yourself or someone else for the stressful experience or what happened after it",
            "Having strong negative feelings such as fear, horror, anger, guilt, or shame",
            "Loss of interest in activities that you used to enjoy",
            "Feeling distant or cut off from other people",
            "Trouble experiencing positive feelings",
            "Irritable behavior, angry outbursts, or acting aggressively",
            "Taking too many risks or doing things that could cause you harm",
            "Being super alert or watchful or on guard",
            "Feeling jumpy or easily startled",
            "Having difficulty concentrating",
            "Trouble falling or staying asleep"
        ]
        
        # Create questions and options
        for i, question_text in enumerate(pcl5_questions, 1):
            question, created = Question.objects.get_or_create(
                assessment=pcl5,
                order=i,
                defaults={
                    'text': question_text,
                    'question_type': 'likert',
                    'weight': 1.0
                }
            )
            
            if created:
                # Create Likert options for each question
                likert_options = [
                    ("Not at all", 0),
                    ("A little bit", 1),
                    ("Moderately", 2),
                    ("Quite a bit", 3),
                    ("Extremely", 4)
                ]
                
                for order, (option_text, value) in enumerate(likert_options, 1):
                    LikertOption.objects.get_or_create(
                        question=question,
                        order=order,
                        defaults={
                            'text': option_text,
                            'value': value
                        }
                    )
        
        # Create PCL-5 Recommendations
        pcl5_recommendations = [
            {
                'min_score': 0, 'max_score': 30, 'risk_level': 'none',
                'title': 'Minimal PTSD Symptoms',
                'description': 'Your responses suggest minimal or no PTSD symptoms.',
                'action_items': '• Continue healthy coping strategies\n• Maintain support networks\n• Practice stress management\n• Consider regular mental health check-ins'
            },
            {
                'min_score': 31, 'max_score': 49, 'risk_level': 'mild',
                'title': 'Mild PTSD Symptoms',
                'description': 'Your responses suggest mild PTSD symptoms that may benefit from attention.',
                'action_items': '• Consider speaking with a mental health professional\n• Practice grounding techniques\n• Maintain regular routines\n• Engage in supportive relationships\n• Learn trauma-informed coping strategies'
            },
            {
                'min_score': 50, 'max_score': 64, 'risk_level': 'moderate',
                'title': 'Moderate PTSD Symptoms',
                'description': 'Your responses suggest moderate PTSD symptoms that warrant professional evaluation.',
                'action_items': '• Schedule evaluation with trauma specialist\n• Consider trauma-focused therapy\n• Practice safety and grounding techniques\n• Maintain support system\n• Avoid alcohol and substance use'
            },
            {
                'min_score': 65, 'max_score': 80, 'risk_level': 'severe',
                'title': 'Severe PTSD Symptoms',
                'description': 'Your responses suggest severe PTSD symptoms that require immediate professional intervention.',
                'action_items': '• Seek immediate professional help\n• Consider specialized trauma treatment\n• Medication evaluation may be helpful\n• Intensive therapy recommended\n• Ensure safety and crisis planning'
            }
        ]
        
        for rec_data in pcl5_recommendations:
            Recommendation.objects.get_or_create(
                assessment=pcl5,
                min_score=rec_data['min_score'],
                max_score=rec_data['max_score'],
                defaults=rec_data
            )

        self.stdout.write(self.style.SUCCESS('All assessments created successfully!'))