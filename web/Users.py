"""
Data model classes for Labs at Yale.

This module defines Python classes that represent key entities in the Labs at Yale
database: Users, Faculty, Labs, and Fellowship. Each class includes attribute
accessors, tuple conversion, and dictionary serialization methods.

Classes:
    - Users: Represents a general user.
    - Faculty: Represents a faculty member with a department field.
    - Labs: Represents a research lab and its metadata.
    - Fellowship: Represents a fellowship opportunity offered by a lab.
"""
from flask_login import UserMixin


# add class application
#fellowship info with apply?

class Users:
    """
      Represents a general user in the Labs at Yale system.

      Attributes:
          net_id (str): The Yale NetID of the user.
          first_name (str): The user's first name.
          last_name (str): The user's last name.
          email (str): The user's Yale email address.
    """
    def __init__(self, net_id, first_name, last_name, email, role):
        """
           Initialize a Users object.

           Args:
               net_id (str): The Yale NetID.
               first_name (str): First name of the user.
               last_name (str): Last name of the user.
               email (str): Email address of the user.
        """
        self.net_id = net_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.role = role

    def get_net_id(self):
        return self.net_id

    def get_first_name(self):
        """Return the user's first name."""
        return self.first_name

    def get_last_name(self):
        """Return the user's last name."""
        return self.last_name

    def get_email(self):
        """Return the user's email address."""
        return self.email

    def get_role(self):
        return self.role

    def to_tuple(self):
        """Return a tuple representation of the user."""
        return (self.net_id, self.first_name, self.last_name, self.email, self.role)

    def to_dict(self):
        """Return a dictionary representation of the user."""
        return {'net_id': self.net_id, 'first_name': self.first_name, 'last_name': self.last_name, 'email': self.email, 'role': self.role}

class AuthUser(Users, UserMixin):
    def get_id(self):
        return self.net_id

class Faculty:
    """
       Represents a faculty member at Yale.

       Attributes:
           net_id (str): The Yale NetID of the faculty member.
           first_name (str): Faculty member's first name.
           last_name (str): Faculty member's last name.
           email (str): Faculty member's email address.
           department (str): Department or academic field.
    """
    def __init__(self, net_id, first_name, last_name, email, department):
        """
               Initialize a Faculty object.

               Args:
                   net_id (str): The Yale NetID.
                   first_name (str): Faculty member's first name.
                   last_name (str): Faculty member's last name.
                   email (str): Faculty member's email.
                   department (str): Department name.
        """
        self.net_id = net_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.department = department

    def get_first_name(self):
        """Return the faculty member's first name."""
        return self.first_name

    def get_last_name(self):
        """Return the faculty member's last name."""
        return self.last_name

    def get_email(self):
        """Return the faculty member's email address."""
        return self.email

    def get_department(self):
        """Return the faculty member's department."""
        return self.department

    def to_tuple(self):
        """Return a tuple representation of the faculty member."""
        return (self.net_id, self.first_name, self.last_name, self.email, self.department)

    def to_dict(self):
        """Return a dictionary representation of the faculty member."""
        return {'net_id': self.net_id, 'first_name': self.first_name, 'last_name': self.last_name, 'email': self.email, 'department': self.department}


class Labs:
    """
        Represents a research lab at Yale.

        Attributes:
            lab_num (int): Unique identifier for the lab.
            lab_name (str): Name of the lab.
            faculty_name (str): Name of the lab's faculty head.
            email (str): Email of the faculty or lab contact.
            field (str): Research field or department.
            description (str): Description of the lab's focus and work.
            website (str): URL for the lab's official website.
            location (str): Physical location of the lab on campus.
    """
    def __init__(self, lab_num, lab_name, faculty_name, email, field, description, website, location):
        """
        Initialize a Labs object.

        Args:
            lab_num (int): Lab identifier number.
            lab_name (str): Name of the lab.
            faculty_name (str): Faculty leader's name.
            email (str): Contact email.
            field (str): Field of research or department.
            description (str): Summary of lab research.
            website (str): Lab website URL.
            location (str): Lab's physical location.
        """
        self.lab_num = lab_num
        self.lab_name = lab_name
        self.faculty_name = faculty_name
        self.email = email
        self.field = field
        self.description = description
        self.website = website
        self.location = location

    def get_lab_num(self):
        """Return the lab number."""
        return self.lab_num

    def get_lab_name(self):
        """Return the lab name."""
        return self.lab_name

    def get_faculty_name(self):
        """Return the faculty leader's name."""
        return self.faculty_name

    def get_description(self):
        """Return the lab description."""
        return self.description

    def get_website(self):
        """Return the lab's website URL."""
        return self.website

    def get_email(self):
        """Return the lab's contact email."""
        return self.email

    def get_location(self):
        """Return the lab's physical location."""
        return self.location

    def get_field(self):
        """Return the lab's research field."""
        return self.field

    def to_tuple(self):
        """Return a tuple representation of the lab."""
        return (self.lab_num, self.lab_name, self.faculty_name, self.email, self.field, self.description, self.website, self.location)

    def to_dict(self):
        """Return a dictionary representation of the lab."""
        return {'lab_num': self.lab_num, 'lab_name': self.lab_name, 'faculty_name': self.faculty_name, 'email': self.email, 'field': self.field, 'description': self.description, 'website': self.website, 'location': self.location}


class Fellowship:
    """
       Represents a fellowship opportunity offered by a Yale lab.

       Attributes:
           fellowship_id (int): Unique ID for the fellowship.
           fellowship_name (str): Name of the fellowship.
           lab_name (str): Name of the lab offering the fellowship.
           faculty_name (str): Faculty advisor for the fellowship.
           class_years (str): Eligible class years
           description (str): Details about the fellowship opportunity.
           deadline (str): Application deadline
           stipend (str): Amount or description of stipend provided.
    """
    def __init__(self, fellowship_id, fellowship_name, lab_name, faculty_name, class_years, description, deadline, stipend, application_count):
        """
        Initialize a Fellowship object.

        Args:
            fellowship_id (int): Fellowship identifier.
            fellowship_name (str): Name of the fellowship.
            lab_name (str): Associated lab name.
            faculty_name (str): Faculty supervisor name.
            class_years (str): Eligible class years.
            description (str): Fellowship description.
            deadline (str): Application deadline.
            stipend (str): Stipend details.
        """
        self.fellowship_id = fellowship_id
        self.fellowship_name = fellowship_name
        self.lab_name = lab_name
        self.faculty_name = faculty_name
        self.class_years = class_years
        self.description = description
        self.deadline = deadline
        self.stipend = stipend
        self.application_count = application_count


    def get_fellowship_id(self):
        """Return the fellowship ID."""
        return self.fellowship_id

    def get_fellowship_name(self):
        """Return the fellowship name."""
        return self.fellowship_name

    def get_lab_name(self):
        """Return the lab name associated with this fellowship."""
        return self.lab_name

    def get_faculty_name(self):
        """Return the faculty supervisor's name."""
        return self.faculty_name

    def get_class_years(self):
        """Return eligible class years for the fellowship."""
        return self.class_years

    def get_description(self):
        """Return the fellowship description."""
        return self.description

    def get_deadline(self):
        """Return the application deadline."""
        return self.deadline

    def get_stipend(self):
        """Return the fellowship stipend details."""
        return self.stipend

    def get_application_count(self):
        """Return the number of applications submitted for this fellowship."""
        return self.application_count

    def to_tuple(self):
        """Return a tuple representation of the fellowship."""
        return (self.fellowship_id, self.fellowship_name, self.lab_name, self.faculty_name, self.class_years, self.description, self.deadline, self.stipend, self.application_count)

    def to_dict(self):
        """Return a dictionary representation of the fellowship."""
        return {'fellowship_id': self.fellowship_id, 'fellowship_name': self.fellowship_name, 'lab_name': self.lab_name, 'faculty_name': self.faculty_name, 'class_years': self.class_years, 'description': self.description, 'deadline': self.deadline, 'stipend': self.stipend, 'application_count': self.application_count}

class Application:
    """
    Represents a student's application to a fellowship, including fellowship details.

    Attributes:
        application_id (int): Unique ID for the application.
        student_net_id (str): Net ID of the student who applied.
        fellowship_id (int): ID of the fellowship applied to.
        fellowship_name (str)
        lab_name (str)
        faculty_name (str)
        class_years (str)
        description (str)
        deadline (str)
        stipend (str)
        status (str): Application status ('applied', 'accepted', 'rejected').
        applied_at (str): Timestamp of application.
        questions (str): Student’s answers or personal statement.
    """

    def __init__(self, application_id, student_net_id, fellowship_id, fellowship_name,
                 lab_name, faculty_name, class_years, description, deadline, stipend,
                 status='applied', applied_at=None, questions=''):
        self.application_id = application_id
        self.student_net_id = student_net_id
        self.fellowship_id = fellowship_id
        self.fellowship_name = fellowship_name
        self.lab_name = lab_name
        self.faculty_name = faculty_name
        self.class_years = class_years
        self.description = description
        self.deadline = deadline
        self.stipend = stipend
        self.status = status
        self.applied_at = applied_at
        self.questions = questions

    def get_application_id(self): return self.application_id
    def get_student_net_id(self): return self.student_net_id
    def get_fellowship_id(self): return self.fellowship_id
    def get_fellowship_name(self): return self.fellowship_name
    def get_lab_name(self): return self.lab_name
    def get_faculty_name(self): return self.faculty_name
    def get_class_years(self): return self.class_years
    def get_description(self): return self.description
    def get_deadline(self): return self.deadline
    def get_stipend(self): return self.stipend
    def get_status(self): return self.status
    def get_applied_at(self): return self.applied_at
    def get_questions(self): return self.questions

class Applicant:
    """
    Represents a student application to a fellowship.
    """
    def __init__(self, application_id, student_net_id, student_first_name, student_last_name, email,
                 major, class_year, status, applied_at, questions):
        self.application_id = application_id
        self.student_net_id = student_net_id
        self.student_first_name = student_first_name
        self.student_last_name = student_last_name
        self.email = email
        self.major = major
        self.class_year = class_year
        self.status = status
        self.applied_at = applied_at
        self.questions = questions

    # Getters
    def get_application_id(self): return self.application_id
    def get_student_net_id(self): return self.student_net_id
    def get_student_first_name(self): return self.student_first_name
    def get_student_last_name(self): return self.student_last_name
    def get_email(self): return self.email
    def get_major(self): return self.major
    def get_class_year(self): return self.class_year
    def get_status(self): return self.status
    def get_applied_at(self): return self.applied_at
    def get_questions(self): return self.questions
