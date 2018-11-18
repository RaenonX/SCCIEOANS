# IE Office Appointment Notifying System (IEOANS)
This system is designed to let students know that it is their turn for the appointment. This idea inherited from the existing people calling system in the Cashier.

_All contents are subject to change._

## Contents
* [Objective](#Objective)
* [Tools](#tools)
* [Program Structure](#program-structure)

## Objective
To create a system which can notify people that it is going to be their turn, they should head to the IE office.
### Pending Additional Function
* Let users know their appointment queue position
* Notify users when their appointment date/time is close
* Let users schedule an appointment through this portal
* Let users can directly contact advisors (or just add a button with a mailto protocol hyperlink)
* Let users access some frequently used functions on the school official website, such as class schedule and transcripts, in their language, as these webpages are not mobile friendly

## Tools
### Frontend Language: HTML, CSS, javascript, jQuery, bootstrap3
No exception, all webpages requires HTML. CSS and bootstrap3 will make the looking of the website beautiful; javascript and jQuery can let our webpage be more interactive.
> The reason of using bootstrap 3 is because that Flask-bootstrap are currently only support this version.
### Backend Language: Python 3
The reason of using Python 3 is because:
* This is the language which CS 121 student is using, and it also can implement things which is taught in CS 141 and CS 143.
* PyPI contains a lot of package, which potentially means the availability of extension.
* The program/system is not performance oriented.
* The language is supported on Heroku, and also the website is easier to build and maintain.
### Server: Heroku (Temporary)
 Heroku is a PaaS platform, which allows us to operate a website without owning an actual server. 
### Website Framework: Python Flask
This framework is easy to build and extend. Also, this is the framework which I familiar with.
### Database: MongoDB (Temporary)
This is a noSQL db, the reason I choose this is because that it can store data with different scheme in a same collection (which can be considered table in SQL). It also provides a Python package for connecting between the program and the database. The biggest advantage is that their free plan already provided 512 MB storage, which I never used 5% of the storage they provided.

## Program Structure
### Frontend
#### Cookie
The program will create a session (cookie) locally to record:
* Login key - This will be generated/refreshed each time the user logged in

#### Endpoints
We are going to create a few endpoints for different usage (The name and the structure of the endpoints are subject to change):
* Main Page
    * [/index (Homepage)](#index)
* Main Portals
    If the user clicked the portal button in the [Homepage](#index) and their identity match what they clicked, then they can skip the step of login. Otherwise, request the user to login.
    * [/student](#student)
    * [/advisor](#advisor)
    * [/staff](#staff)
    * [/user](#user)

#### /index
The main page of the website. This will mainly have three buttons to navigate to the "role specific" page, such as advisor's, staff's and student's. These pages will contain the function that the user needs.
Also, this page will have some brief summary of the current status or the information of the IE office:
* Current waiting / Current available / Current avg. meeting duration
* Is IE office open or not
* How many advisors available (Express and Regular)
* Logout (If logged in)
#### /student
This page will have some way to access the functions below:
* Schedule an appointment
* Send message to the advisors
* Lineup to the system
* Changing their information logged on the system
* Find their appointment records
* Add notes to the appointments
Note: As the student lined up to the queue or scheduled an appointment, they can add some notes to let the advisor prepare before the meeting starts.
#### /advisor
This page will have some way to access the functions below:
* Know some information about the student
* Record the start time and the end time of the meeting
#### /staff
This page will have some way to access the functions below:
* Detailed stats of the meeting record
#### /user
This domain does not have the page for "index," but this is the domain which contains some identity processing related functions.

### Backend
Basically the system will have these databases (Bolded item is the index of the database):
* Appointments Record
    * **Serial number**
    * Scheduled (Optional)
        * Scheduled Timestamp 
        * Scheduled time to meet
        * Scheduled time to end
    * Lined-up Timestamp
    * Meeting Start/End Timestamp
    * Student ID
    * Purpose
    * Advisor
    * Specified Advisor
    * Notes

* Accounts
	* Identity (Staff/Advisor/Student)
	* Account ID
	* Account Password (Defined by user, store in SHA224)
	* Account Recovery Email
	* Student ID (If the identity is student)
	* Login key in use

[Some of the data fields might be deleted if the system is allowed to connect to the database of the school]
* Student information
    * **Student ID**
	* Name
	* Name Pronounciation
	* Language
		* Languages
		* Primary Language
	* Phone
		* Phone number
		* Carrier 
	* Email
		* Email address(es)
	* Notification Preferences
		* SMS
		* Email 
		* Manually Call

**Waiting queue** and the **current running appointment** is cached locally after the meeting record database is updated or the system has rebooted.
The waiting queue is categorized by the viewing purpose, so **it's not a single line**.

### Case Handling / Functions
#### Statistics Page (In /staff)
* Filter by Date Range, Advisor, Category and Student.
* Display brief summary, which contains the average and median length of the meetings, number of the records (How many appointments inside), and also the raw data
* Add functionality to exclude/delete/edit specific raw data in the database and view.

#### Advisor Portal (/advisor)
* Notify advisor to sign out/log the end meeting time after certain period of time (default could be 45 mins).

#### Staff queue arranging
* Allow staff to manually "start" the meeting, and make thi action reversible.

## Notes
* Ask Ray ([RaenonX JELLYCAT](https://shorelinecsclub.slack.com/messages/@UBB160092)) on Slack for program implementation details.
* If you want to join this project, please also contact Ray ([RaenonX JELLYCAT](https://shorelinecsclub.slack.com/messages/@UBB160092)) on Slack. Anyone want to join this project must join Shoreline CC CS Club. No requirements for joining the project.
* Pending TODO:
	* /user/register
		* Add multiple entries functionality of the Email Field (Student Only)
		* Add multiple entries functionality of the Language Field (Student Only)
		* Add multiple entries functionality of the Phone Field (Student Only)