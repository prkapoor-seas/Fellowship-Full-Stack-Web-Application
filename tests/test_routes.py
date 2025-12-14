"""
uses monkeypatching to test fake data
"""
class FakeLabs:
    def __init__(self, lab_number, name, faculty, email, field, description, website, location):
        self._lab_num = lab_number
        self._name = name
        self._faculty = faculty
        self._email = email
        self._field = field
        self._desc = description
        self._website = website
        self._loc = location

    def get_lab_num(self): 
        return self._lab_num
    def get_lab_name(self): 
        return self._name
    def get_faculty_name(self): 
        return self._faculty
    def get_email(self): 
        return self._email
    def get_field(self): 
        return self._field
    def get_description(self): 
        return self._desc
    def get_website(self): 
        return self._website
    def get_location(self): 
        return self._loc

def test_labs_page_renders(client, monkeypatch):
    dummy_labs = [
        FakeLabs(
            lab_number=1,
            name="Alan Weide if you are reading this, hi",
            faculty="Toastie",
            email="toaster.toastie@yale.edu",
            field="Dog Park",
            description="My dog is the cutest dog ever and you can't tell me otherwise",
            website="<a href='https://www.youtube.com/watch?v=rTgj1HxmUbg'>Site</a>",
            location="STW 707"
        )
    ]

    def fake_get_labs_information(q=None):
        return dummy_labs

    # learned this in 327 but when we get the labs information, it uses our fake function instead
    # we still send the request to /labs though 
    monkeypatch.setattr("fellowship.get_labs_information", fake_get_labs_information)

    resp = client.get("/labs")

    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "Alan Weide if you are reading this, hi" in html
    assert "Toastie" in html
    assert "Dog Park" in html

        
# fellow_name = request.form.get('fellow_name')
# description = request.form.get('description')
# deadline = request.form.get('deadline')
# stipend = request.form.get('stipend')
# class_years = request.form.getlist('class_year[]')

# @app.route('/fellowships')
# def fellowships():
#     q = (request.args.get('q') or "").strip()
#     f = get_fellowship_information(q)
#     fellowship_id = _get_faculty_fellowship_id() if current_user.is_authenticated and current_user.role == 'faculty' else None
#     return render_template('fellowships.html', fellowships_list=f, q=q, fellowship_id=fellowship_id)

class FakeFellowship:
    """
    Produces a fake fellowship to getting the fellowship information and gets the data from the client
    use fake data instead of the database since the database could change
    """
    def __init__(self, fellow_name, description, lab, deadline, stipend, faculty, class_years):
        self._fellow_name = fellow_name
        self._description = description
        self._deadline = deadline
        self._stipend = stipend
        self._class_years = class_years
        self._lab = lab
        self._faculty = faculty
    
    def get_lab_name(self):
        return self._lab

    def get_fellowship_name(self):
        return self._fellow_name
    
    def get_description(self):
        return self._description

    def get_deadline(self):
        return self._deadline
    
    def get_stipend(self):
        return self._stipend
    
    def get_class_years(self):
        return self._class_years

    def get_faculty_name(self):
        return self._faculty
    

def test_fellowship_page_renders(client, monkeypatch):
    dummy_fellowships = [
        FakeFellowship(
            fellow_name="Fellowship something something",
            description="Test fellowship stuff",
            lab="Yah Yeet Lab",
            deadline="2024-01-01",
            stipend="$9999",
            faculty="Sugar Doggo",
            class_years="2027, 2025",
        )
    ]

    def fake_get_fellowship_information(q=None):
        return dummy_fellowships
    
    monkeypatch.setattr("fellowship.get_fellowship_information", fake_get_fellowship_information)
    resp = client.get("/fellowships")

    assert resp.status_code == 200
    html = resp.data.decode("utf-8")
    assert "Fellowship something something" in html
    assert "Test fellowship stuff" in html
    assert "2024-01-01" in html
    assert "$9999" in html
    assert "2025" in html

# have a second database for testing --> mirrors to some degree
# the real database -- edge case items that have good test cases

class FakeFaculty:
    def __init__(self, first_name, last_name, email, department, office_location):
        self._first_name = first_name
        self._last_name = last_name
        self._email = email
        self._department = department
        self._office_location = office_location

    def get_email(self):
        return self._email

    def get_department(self):
        return self._department

    def get_office_location(self):
        return self._office_location

    def get_first_name(self):
        return self._first_name
    
    def get_last_name(self):
        return self._last_name
    

def test_faculty_page_renders(client, monkeypatch):
    dummy_faculty = [
        FakeFaculty(
            first_name="Yahoo",
            last_name="Google",
            email="yahoo.google@example.com",
            department="Some Thing Department",
            office_location="Room 67"
        )
    ]

    def fake_get_faculty_information(q=None):
        return dummy_faculty

    monkeypatch.setattr("fellowship.get_faculty_information", fake_get_faculty_information)

    resp = client.get("/faculty")
    assert resp.status_code == 200

    html = resp.data.decode("utf-8")
    assert "Yahoo" in html
    assert "yahoo.google@example.com" in html
    assert "Some Thing Department" in html
