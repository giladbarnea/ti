# from home accident
body = {
	"absence_type": "None",
	"client":       "38",
	"client_name":  "Allot",
	"day_report":   67979,
	"description":  "RSEvents README.md",
	"duration":     "00:42:00",
	"end":          "07:52:00",
	"id":           40429,
	"project":      49,
	"project_name": "Allot",
	"start":        "07:10:00",
	}

# fixed from home to at office
body2 = {
	"approved":         None,
	"date":             "2021-07-28",
	"from_home":        False,
	"id":               67979,
	"is_special_day":   False,
	"is_valid":         True,
	"is_working_day":   True,
	"projects":         [
		{
			"absence_type": "None",
			"client":       "38",
			"client_name":  "Allot",
			"day_report":   67979,
			"description":  "RSEvents README.md",
			"duration":     "00:42:00",
			"end":          "07:52:00",
			"id":           40429,
			"project":      49,
			"project_name": "Allot",
			}]
	"start":            "07:10:00",
	"request_approval": False,
	"type":             "full_day",

	}

# 2nd report same day
body3 = {
	"absence_type": "None",
	"client":       "38",
	"client_name":  "Allot",
	"day_report":   67979,
	"description":  "Merging with Lina's branch, Hagai new API, syncing with Carlos",
	"duration":     "09:20:00",
	"end":          "19:30:00",
	"id":           40431,
	"project":      49,
	"project_name": "Allot",
	"start":        "10:10:00",
	}

# only report tuesday good from home
body4 = {
	"absence_type": "None",
	"client":       "38",
	"client_name":  "Allot",
	"day_report":   67820,
	"description":  "Helped Roman\nAccounts RSEvents callback and listener\nrsevent_model.py fixed whitelist_violation JsonDecodeError with BaseModel __getattribute__ override and __serialize__ class var",
	"duration":     "12:58:00",
	"end":          "22:18:00",
	"id":           40434,
	"project":      49,
	"project_name": "Allot",
	"start":        "09:20:00",
	}

# * Monday
# PUT https://carmitush-prod.herokuapp.com/api/day-reports/2021-07-26/
request_payload = {"date":"2021-07-26","type":"full_day","from_home":false}
auth_bearer = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyMDcsInVzZXJuYW1lIjoiZ2lsYWQuYmFybmVhQGhlcm9sby5jby5pbCIsImV4cCI6MTYyOTc4NjQxNywiZW1haWwiOiJnaWxhZC5iYXJuZWFAaGVyb2xvLmNvLmlsIn0.QDhvA4aytp4zDW23zdCNKW35bRbRMUk8jZtBIsMFd-k"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.115 Safari/537.36"

# POST https://carmitush-prod.herokuapp.com/api/project-reports/
request_payload = {"project":49,"absence_type":"None","day_report":67661,"description":"Meetings: 16.5, 16.4 Merge, Redis introduction 1/2","end":"16:00:00","start":"09:20:00"}

# * Sunday
# POST https://carmitush-prod.herokuapp.com/api/project-reports/
# {"project":49,"absence_type":"None","day_report":67501,"description":"RSEvents Fixed trace_id, continued developing test cases","end":"16:47:00","start":"09:40:00"}

# * Thursday
# PUT https://carmitush-prod.herokuapp.com/api/day-reports/2021-07-22/
# request: {"date":"2021-07-22","type":"full_day","from_home":false}
# response: {"id":67023,"type":"full_day","date":"2021-07-22","user":207,"projects":[],"is_valid":false,"is_working_day":true,"is_special_day":false,"from_home":false,"approved":null,"request_approval":false}

# POST https://carmitush-prod.herokuapp.com/api/project-reports/
# request: {"project":49,"absence_type":"None","day_report":67023,"description":"RSEvents","end":"18:30:00","start":"09:20:00"}
# response: {"id":40495,"start":"09:20:00","end":"18:30:00","description":"RSEvents","day_report":67023,"project":49,"project_name":"Allot","duration":"09:10:00","client_name":"Allot","client":"38","absence_type":"None"}