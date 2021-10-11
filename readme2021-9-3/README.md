# :cat2: TOUCH TYPING APP FOR USE IN SCHOOLS  

## :boy: TAKASHI IZUTA

### :film_strip: Video Demo:  <URL HERE>

## :point_right:  Goal, Motivation and Uniqueness  

 The aim of this project is to implement a flexible and suitable touch typing practicing app for use in schools. 

 This work is motivated by the facts that 
 
 1. most available similar systems are, from the very beginning, embedded with sample texts that can not be changed or customized by the system administrator; 
 
 2. in general no relatively simple means to visualize the students work progress reports and activity logs are available in such systems, which increases the work load of assessing and grading the assignments.

 So, this work fills these gaps and provides a somehow flexible, customizable, simple and easy-to-use app to be used in classes aimed to train students in touch typing skills according to the goals set by the instructor or meeting some specific needs of the students.   

 There are two other striking characteristics that make this app very unique. 

  - The sample text given by the instructor is shown in a different detached browser window, so that the user can place it wherever it is more convenient to see it. 

  - There is a visual representation of a Japanese compatible standard ASCII keyboard layout on which the key being pressed by the user is shown. This allows learners to check their fingers' positions and perform the typewriting tasks without looking at their fingers and the actual keyboard. It is noteworthing that this feature is very important for practing touch typing, otherwise it is most likely that not only will the users uncounsciously acquire the unhealthy and undesirable habit of looking at the fingers but also and, in the future, perhaps even rely heavily on it when typewriting.

 In addition, icons, buttons and other designing resources were originally created by the author himself without relying on others' materials.

 All in all, the outcome of this work is a very useful and practical app that can be used in a pre-entry level information literacy course whose goal is to train learners in the typewriting skill. 

 It might sound naive or even exaggerated, but since, in general, any IT related activity starts on a keyboard or some similar devices and end up relying on the user's typewriting skills, the potential contribution of this app is, so to speak, incomputable!  

## :point_right: Basic Specification 

 The app was implemented with python, JavaScript, sqlite3, html and css running on a flask based web server.

 It is designed to be used on a desktop or laptop computer equipped with a standard display device. It is not recommeded to be used on mobile smartphones and alike.

 The app displays the weather information related to the user browser's geolocation on the title bar. This information is resquested from an external web service [openweathermap](https://openweathermap.org/) through previous acquisition of an API KEY. Moreover, the geolocation is obtained by a JavaScript snippet when the user registers or logs in into the system.

 There is also a dark window functionality available through clicking on the icon displayed on the right side of the window. It is part of a free software license [jsdelivr](https://cdn.jsdelivr.net/) and is accessed by a piece of JavaScript code.  

## :point_right:  System Structure 

### :smile_cat: Preliminaries

 Before you begin, it is suggested that you get an API key at [openweathermap](https://openweathermap.org/) and set the variable WEATHER_API in 'application.py' at line 39. 
 
 Note that it is fine if no API key is set. The only difference is that, without it, the weather info on the title bar of the app will show only headlines.   

 If you want to change the number of texts, just reset the default value of NUMBER_OF_TEXTS in 'application.py' at line 44. However if you change it here you will also have to change 'index.html' a bit. To do so, just open 'index.html' and follow the directions.

 If you want to rename the database file and administrator's user name, which are defined by variables ADMIN_USER_NAME and DB_NAME, respectively  in 'application.py', you have to set back the system to its initial condition. 
 
 That is to say, delete entirely the folders 'admin_folder', 'users_folder' and 'touch_typing.db' on your system folder.

 Be aware, if you delete the system folders, all your sample files and undergoing typewriting task files will be deleted. So, do it only at the very beginning of system introduction without any user already signed up. :warning: More importantly, do it at your own risk and on your sole responsability.

### :smile_cat: Running Up
 
 Once you set up your system, open a console window and move to the directory where 'application.py' is stored. Then start up by typing 'flask run' on your console.
 
 Immediately after you run up the system, the pieces of python codes in the upper part of 'application.py' are executed.
 
  Firstly, they create the database file if it does not exist. Then, tables 'users', 'user_input' and 'history' are created in case they do not exist.
  
  Table 'users' is used to store users' info and it has the following structure:
  
  - id: INTEGER PRIMARY KEY AUTOINCREMENT
  - user_name: TEXT NOT NULL
  - user_password: TEXT NOT NULL
  - register_date DEFAULT CURRENT_TIMESTAMP NOT NULL
  
 Table 'user_input' is used to store users' current status of the typewriting tasks. Its fields are
 
  - id: INTEGER PRIMARY KEY AUTOINCREMENT
  - user_id: INTEGER NOT NULL
  - user_name: TEXT NOT NULL
  - input_file_name: TEXT NOT NULL
  - input_done: NUMERIC NOT NULL
  - input_match: NUMERIC NOT NULL
  - last_update: DEFAULT CURRENT_TIMESTAMP NOT NULL
 
 Table 'history' stores the activities on the system. It is composed by the fields
 
 - id: INTEGER PRIMARY KEY
 - user_id: INTEGER NOT NULL
 - activity: TEXT NOT NULL
 - last_update DEFAULT CURRENT_TIMESTAMP NOT NULL
 
 Secondly, if the administrator is not in the table, it is inserted.

 Finally, check whether the folders 'admin_folder' and 'users_folders' exist. If not, create them and inside them create administrator's folder. Also, create samples files inside folder 'admin_folder/admin' and typewriting task files in 'users_folder/admin'.

 Note that 'users_folder/admin' folder and typewriting task files are created by function 'mkdir_mkfile(user_id, user_name, user_folder, user_file)'.

 Actually, this function 'mkdir_mkfile' is called every time a new user joins to the system as a user. 

### :smile_cat: Login Window

 When the users access the app, the first window that they will see is 'login.html'. 
 
 ![login screen](login.png)

 Inside 'login.html' there is a JavaScript snippet that will detect the geolocation of the browser in order to display the weather info once you are logged in.

 If you click on 'login' button, it will call function 'login' in 'application.py'. This function checks whether the user name and password are correctly filled in. 

 If everything is correctly sent to the function, login procedure is established. At this point a 'session' is started and browser's local weather information is requested.
 
 The acquisition of the weater info is performed by function 'weather_info' in 'application.py'.
 
 If an error is detected, a message window will be shown, and the user will have to start all over again from the very first window.

 Finally, pay attention to the details of the designing work of the windows, the icons and the buttons, these assets were all designed and drawn by the author himself.

### :smile_cat: Register Window

 New users will have to click on 'register' button and fill up the form in 'register.html'

 ![register screen](register.png)

 A piece of JavaScript will check whether the lenght of the password is greater than 7 letters and whether it includes not only letters, but also at least a number.  If not, button 'register' is disabled.

 Pressing button 'register' will call function 'register' in 'application.py'. This function checks whether user id is available, and whether the input passwords coincide. 
 
 If all the information is correct the funtion calls function 'mkdir_mkfile' in 'application.py' in order to create user's folder and typewriting task files.
 
 The last processing of function 'register' is to call function 'index' in 'application.py', which will render 'index.html'

 Once you signed up, they log in into the system. 

 Actually, if you press ‘register’, the next window to be displayed will be the same as when you log in.

 Also, when you press ‘register’, a JavaScript snippet will catch the browser’s geolocation in order to request and display the weather forecast.

### :smile_cat: Index Window

 When you log in as the administrator, you will have a window a little bit different from other users.
 
 The window consists of four independent areas. Of them, only the second area will be displayed to all users. 
 
 The upper area is used to store and update the sample texts that users will have to input as assignments.    

 The second area shows the user’s current work status report. It is the same as shown to other users. The fields ‘done’ and ‘match’ are the results of user’s input relatively to the sample text, which has been assigned by the instructor. These computations are dealt with by function 'index' in 'application.py'

Students begin to do their assignments by selecting the input text and pressing ‘submit’.


 The third area displays the work reports of all users. This allows the administrator to check and grade the students’ performances.

 The area at the bottom shows the activities of all users. So that, the administrator can see the past and current activities of all users. 

 ![index1 screen](index1.png)
 ![index2 screen](index2.png)
 ![index3 screen](index3.png)

 If you, as an administrator, want to store a new sample or update an existing sample file, you will have firstly to choose the sample file and click on 'submit', which will trigger function 'sample_file_to_update' in 'application.py'. This function will retrieve the sample file from the system, open it and read its content. Then, the content is returned back to the text area in 'index.html'. 
 
 After changing or adding something into the text area, you will have to click on ‘save’ button. This action will call function 'save_sample_text' in 'application.py'. Basically, it updates the sample file and records this action in the table 'history'.
 
 If the sample text is correctly stored in its file, the window comes back with empty text area.

 ![update sample screen](update_sample.png)

 If you, as the administrator, want to have an overview of all users' typewriting tasks progress, press 'show' button. It will call function 'show_all_work_in_progess' in 'application.py', which will retrieve and come back to this page with info from table 'user_input'. 
 
 if you click on 'hide', it will call function 'hide_all_work_in_progess' in 'application.py', and come back empty to this window. 

 ![show_all_work_in_progess](all_progress.png)

 Likewise, you press on 'show' button to call function 'show_all_activities' in 'application.py'. It will retrieve all the records from table 'history' and show all the activities since the time you introduced the system. 
 
 On the other hand, if you click on 'hide' button, it will call function 'hide_all_activities' in 'application.py', which will return empty info.

 ![show_all_activities](all_activities.png)

 Finally, if you want to typewrite into your task file, choose the file and press on 'submit'. It will call function 'choose_your_text_to_input' in 'application.py', which will open the selected file and read its content as well as retrieve the info to be passed to 'input_text.html'

 ![input_text](select_input_file.png)

### :smile_cat: Input Text Window

 If the user has previously input something, the text will be displayed on the text area. 

 To begin with, the user will have to click on ‘show’ button to pop up the sample window, which is executed by a piece of JavaScript code in 'keyboard.js'.

 ![input_file](input_file.png)

 Once you have the sample text on the screen, all you have to do is to write down the sample text onto the input text area.

 The keyboard layout drawn down the text area will show which key is being pressed. This is carried out by a JavaScript snippet in 'keyboard.js'. 
 
 Actually, there are also JavaScript snippets disabling copy and paste functions in 'disable_key.js'.

 To update the input file, the user will have to click on ‘save’ button that will call function 'update_my_input_file' in 'application.py'. 
 
 Function 'update_my_input_file' will update the input file and table 'history'; then come back again to this screen with updated text.

### :smile_cat: History Window

 If you click on ‘history’ tab on the title bar, you will see all your activities since you signed up. 
 
 This button is linked to function 'history' in 'application.py'. Essentially, after retrieving records from table 'history', it renders 'history.html'. 

 This allows users to check all their activities when necessary. 

 ![history](history.png)

### :smile_cat: Chang Password Window

 Clicking on 'change password' on the title bar will call function 'change_password' in 'application.py'.

 ![change_password](change_password.png)

 Users are allowed to change only their passwords. In order to do so, they will have to be logged in with their own user ids as well as fill up their current passwords in the form.

 However, if you are the administrator you can change anyone’s password.

 Actually, even though the system administrator can change anyone’s password without knowing their current passwords, the administrator will have to input at least one letter into the ‘current password’ area in order to proceed.

 Basically, function 'change_password' retrieves info from table 'users' and if everything is right, it updates the table. needless to say that this function updates table 'history'.
 
 ### :smile_cat: Logout Window

 Finally, if you press on ‘log out’ button, it will call function 'logout' in 'application.py' to clear and finish your session.  
 
 Moreover, when you press it, the login window will come up.

 ![logout](logout.png)

 ## :warning: Disclaimer
 
  This app is provided "as is" and without warranty of any kind. The author of this project does not assume any responsability for damage or risk and does not provide any kind of support or feedback whatsoever.
 
  Once you use this app, you fully agree unconditionally that it is completely at your own risk and on your sole responsability.
  
  Thus, it is understood that you will never, legally or not, blame this app for whatever you obtain.   