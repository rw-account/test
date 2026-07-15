from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DecimalField, IntegerField, TextAreaField
from wtforms.validators import (
    DataRequired,
    Length,
    Regexp,
    NumberRange,
    optional,
)

class LoginForm(FlaskForm):
    username = StringField(
                            'اسم المستخدم',
                            validators=[
                                DataRequired(message="اسم المستخدم مطلوب"),
                                ])
    password = PasswordField(
                            'كلمة المرور', 
                            validators=[
                                DataRequired(message="كلمة المرور مطلوبة"),
                                ])
    submit = SubmitField('تسجيل الدخول')



    
class RegistrationForm(FlaskForm):
    username = StringField(
        'اسم المستخدم',
        validators=[
            DataRequired(message="اسم المستخدم مطلوب"),
            Length(min=3, message="اسم المستخدم يجب أن يكون 3 أحرف على الأقل"),
        ]
    )
    password = PasswordField(
        'كلمة المرور',
        validators=[
            DataRequired(message="كلمة المرور مطلوبة"),
            Length(min=8, max=128, message="كلمة المرور يجب أن تكون بين 8 و 128 حرف"),
            Regexp(
                r'(?=.*[A-Za-z\u0600-\u06FF])(?=.*[^A-Za-z0-9\u0600-\u06FF])', 
                message="كلمة المرور يجب أن تحتوي على حرف واحد على الأقل ورمز واحد على الأقل"
            ),
        ]
    )

    submit = SubmitField('انشاء حساب جديد')


class ProductForm(FlaskForm):
    name = StringField(
        'اسم المنتج ',
        validators=[
            DataRequired(message="اسم المنتج مطلوب"),
            Length(min=1, max=100, message="اسم المنتج يجب أن يكون بين 1 و 100 حرف"),
        ],
    )
    price = DecimalField(
        'السعر (دولار) ',
        places=2,
        validators=[
            DataRequired(message="السعر مطلوب"),
            NumberRange(min=0.01, max=100000, message="السعر غير صالح")
        ],
    )
    quantity = IntegerField(
        'الكمية*',
        validators=[
            DataRequired(message="الكمية مطلوبة"),
            NumberRange(min=1, max=100000, message="الكمية يجب أن تكون بين 1 و 100000")
        ],
    )
    description = TextAreaField(
        "الوصف",
        validators=[
            optional(),
            Length(max=1000, message="الوصف طويل جدًا"),
        ]
        
    )
    submit = SubmitField('إضافة المنتج')


class MovementForm(FlaskForm):

    quantity = IntegerField(
        'الكمية',
        validators=[
            DataRequired(message="الكمية مطلوبة"),
            NumberRange(min=1, max=100000, message="الكمية يجب أن تكون بين 1 و 100000"),
        ],
    )