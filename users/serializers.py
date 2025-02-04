from django.db import transaction
from django.contrib.auth.models import Group
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from academic.models import Teacher, Subject, Parent
from .models import CustomUser, Accountant



class UserSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)
    isAccountant = serializers.SerializerMethodField(read_only=True)
    isTeacher = serializers.SerializerMethodField(read_only=True)
    isParent = serializers.SerializerMethodField(read_only=True)
    accountant_details = serializers.SerializerMethodField(read_only=True)
    teacher_details = serializers.SerializerMethodField(read_only=True)
    parent_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "middle_name",
            "last_name",
            "isAdmin",
            "isAccountant",
            "isTeacher",
            "isParent",
            "accountant_details",
            "teacher_details",
            "parent_details",
        ]

    def get_isAdmin(self, obj):
        return obj.is_staff

    def get_isAccountant(self, obj):
        return obj.is_accountant

    def get_isTeacher(self, obj):
        return obj.is_teacher

    def get_isParent(self, obj):
        return obj.is_parent

    def get_username(self, obj):
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.email or "Unknown User"

    def get_accountant_details(self, obj):
        """Return accountant details if the user is an accountant."""
        if obj.is_accountant and hasattr(obj, "accountant"):
            return AccountantSerializer(obj.accountant).data
        return None

    def get_teacher_details(self, obj):
        """Return teacher details if the user is a teacher."""
        if obj.is_teacher and hasattr(obj, "teacher"):
            return TeacherSerializer(obj.teacher).data
        return None

    def get_parent_details(self, obj):
        """Return parent details if the user is a parent."""
        if obj.is_parent and hasattr(obj, "parent"):
            return ParentSerializer(obj.parent).data
        return None


class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = UserSerializer.Meta.fields + ["token"]

    def get_token(self, obj):
        try:
            token = RefreshToken.for_user(obj)
            return str(token.access_token)
        except Exception:
            return None


class AccountantSerializer(serializers.ModelSerializer):
    payments = serializers.SerializerMethodField()

    class Meta:
        model = Accountant
        fields = [
            "id",
            "username",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "phone_number",
            "empId",
            "address",
            "gender",
            "national_id",
            "nssf_number",
            "tin_number",
            "date_of_birth",
            "salary",
            "unpaid_salary",
            "payments",
        ]

    def get_payments(self, obj):
        """Lazy import to avoid circular import issue"""
        from finance.serializers import PaymentSerializer  # Import inside method

        if obj.user:
            payments = obj.user.payments.all()
            return PaymentSerializer(payments, many=True).data
        return []

    def validate_email(self, value):
        request = self.context.get("request", None)
        accountant_id = self.instance.id if self.instance else None  # Get accountant ID if updating
        
        if Accountant.objects.filter(email=value).exclude(id=accountant_id).exists():
            raise serializers.ValidationError("A accountant with this email already exists.")
        
        return value

    def validate_phone_number(self, value):
        accountant_id = self.instance.id if self.instance else None  # Get accountant ID if updating

        if Accountant.objects.filter(phone_number=value).exclude(id=accountant_id).exists():
            raise serializers.ValidationError("A accountant with this phone number already exists.")
        
        return value


class TeacherSerializer(serializers.ModelSerializer):
    subject_specialization = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=True
    )
    subject_specialization_display = serializers.StringRelatedField(
        many=True, source="subject_specialization", read_only=True
    )
    payments = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = [
            "id",
            "username",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "phone_number",
            "empId",
            "short_name",
            "subject_specialization",
            "subject_specialization_display",
            "address",
            "gender",
            "national_id",
            "nssf_number",
            "tin_number",
            "date_of_birth",
            "salary",
            "unpaid_salary",
            "payments",
        ]

    def get_payments(self, obj):
        """Lazy import to avoid circular import issue"""
        from finance.serializers import PaymentSerializer  # Import inside method

        if obj.user:
            payments = obj.user.payments.all()
            return PaymentSerializer(payments, many=True).data
        return []

    def validate_email(self, value):
        request = self.context.get("request", None)
        teacher_id = self.instance.id if self.instance else None  # Get teacher ID if updating
        
        if Teacher.objects.filter(email=value).exclude(id=teacher_id).exists():
            raise serializers.ValidationError("A teacher with this email already exists.")
        
        return value

    def validate_phone_number(self, value):
        teacher_id = self.instance.id if self.instance else None  # Get teacher ID if updating

        if Teacher.objects.filter(phone_number=value).exclude(id=teacher_id).exists():
            raise serializers.ValidationError("A teacher with this phone number already exists.")
        
        return value


    def validate_subject_specialization(self, value):
        """
        Validate that all subject names in the input exist in the database.
        Ensure it works for both create and update operations.
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("Subject specialization should be a list of subject names.")

        # Get existing subjects matching the provided names
        existing_subjects = Subject.objects.filter(name__in=value).distinct()

        # Extract names of found subjects
        existing_subject_names = set(existing_subjects.values_list("name", flat=True))

        # Identify missing subjects
        missing_subjects = set(value) - existing_subject_names

        if missing_subjects:
            raise serializers.ValidationError(
                f"The following subjects do not exist: {', '.join(missing_subjects)}"
            )

        return existing_subjects  # Return the queryset instead of a list of names


    def create(self, validated_data):
        subject_specialization_data = validated_data.pop("subject_specialization")
        teacher = Teacher.objects.create(**validated_data)
        subjects = Subject.objects.filter(name__in=subject_specialization_data)
        teacher.subject_specialization.set(subjects)
        return teacher


class ParentSerializer(serializers.ModelSerializer):
    children_details = serializers.SerializerMethodField()

    class Meta:
        model = Parent
        fields = [
            "id",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "phone_number",
            "address",
            "gender",
            "date_of_birth",
            "children_details",
        ]

    def get_children_details(self, obj):
        """Returns a list of children associated with the parent."""
        return [
            {
                "id": child.id,
                "first_name": child.first_name,
                "last_name": child.last_name,
            }
            for child in obj.children.all()
        ]

    def validate_email(self, value):
        """Ensure email uniqueness among parents."""
        if Parent.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A parent with this email already exists."
            )
        return value

    def validate_phone_number(self, value):
        """Ensure phone number uniqueness among parents."""
        if Parent.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError(
                "A parent with this phone number already exists."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        """Creates a Parent and an associated CustomUser."""
        email = validated_data.get("email")
        first_name = validated_data.get("first_name", "")
        last_name = validated_data.get("last_name", "")

        # Create the Parent instance
        parent = Parent.objects.create(**validated_data)

        # If email exists, create a corresponding CustomUser
        if email:
            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_parent": True,
                },
            )
            if created:
                # Set a default password
                default_password = f"{first_name.lower()}{last_name.lower()}123"
                user.set_password(default_password)
                user.save()

                # Assign to "parent" group
                group, _ = Group.objects.get_or_create(name="parent")
                user.groups.add(group)

            # Attach the created user to the parent
            parent.user = user
            parent.save()

        return parent

    @transaction.atomic
    def update(self, instance, validated_data):
        """Updates a Parent and syncs changes to the associated CustomUser."""
        email = validated_data.get("email", instance.email)
        first_name = validated_data.get("first_name", instance.first_name)
        last_name = validated_data.get("last_name", instance.last_name)

        # Update Parent
        parent = super().update(instance, validated_data)

        # If the Parent has an associated CustomUser, update it as well
        if hasattr(parent, "user") and parent.user:
            user = parent.user
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        return parent
