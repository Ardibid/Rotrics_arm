##########################################################################################
###### Imports
##########################################################################################
import json
import numpy as np
import os


##########################################################################################
###### Test Variables
##########################################################################################
raw_data = {
   "drawing":{
      "strokes":[
         [
            {
               "x":100,
               "y":200,
               "a":15,
               "p":0.4
            },
            {
               "x":300,
               "y":400,
               "a":90,
               "p":0.5
            },
            {
               "x":400,
               "y":200,
               "a":125,
               "p":1.
            }
         ],
         [
            {
               "x":600,
               "y":400,
               "a":45,
               "p":0.2
            },
            {
               "x":600,
               "y":300,
               "a":45,
               "p":0.3
            }
         ]
      ]
   }
}


##########################################################################################
###### Classes
##########################################################################################
class Drawing_processor(object):
   """
   Python class to convert a dictionary and into a JSON format and back
   """
   def __init__(self, pressure_factor= -2, base_z = -45, safe_z_val = 0, slider = False ):
      """
      Args:
            pressure_factor (float): a quoefficient to make thickinsses based on pressure on paper
                                       smaller numbers means the difference between the thick and thin
                                       strokes are wider
            base_z (float): the z value of the paper that the robot draws on
            safe_z_val (float):  value that is going to be added to the base_z while the 
                                 drawing tool is not supposed to write on the paper
            slider (boolean): Determines if the robot is on a slider or not, if True, e value will
                              be sent to robot instead of x values.
      """

      # this is the address were the json drawing file will be saved
      self.default_path = "./data/path_data.json"
      
      self.pressure_factor = pressure_factor
      self.safe_z_val = safe_z_val
      self.base_z = base_z
      self.slider = slider
      self.json_object = None

   def draw(self, arm, drawing):
      """
      Send drawing commands to the robot arm
      Args:
         arm (Arm): arm to run the drawing on 
         drawing (numpy.ndarray): list of polylines to draw, i.e.:
                                    [array([[100. , 200. ,  15. ,   0.4],
                                            [300. , 400. ,  90. ,   0.5],
                                            [400. , 200. , 125. ,   1. ]])
                                    array([[6.0e+02, 4.0e+02, 4.5e+01, 2.0e-01],
                                           [6.0e+02, 3.0e+02, 4.5e+01, 3.0e-01]])]
      returns:
         None
      """
      # this key will determine if the robot needs to wait for each
      # motion to finish before sending the next
      wait_key = True

      # just adds a small time delay between each motion
      wait_val = 0.1

      # set the tool as rotary tool
      # arm.set_module_type(6)
   
      # loop over polylines
      for i, poly_line in enumerate(drawing):
         print ("poly line #{}".format(i))

         # at any position, first make sure the pen is away
         # from the paper
         current_pose = arm.get_current_position()

         if self.slider:
            arm.move_to(e= current_pose[3], y= current_pose[1], z = self.safe_z_val, wait= wait_key)
         else:
            arm.move_to(x= current_pose[0], y = current_pose[1], z= self.safe_z_val, wait= wait_key)


         for j, target in enumerate(poly_line):
            print ("\ttarget #{}".format(j))
            x, y, a, p = target
             
            if j == 0:
               # moves towards the first target, without changin z value
               # to avoid touching paper
               if self.slider:
                  print ("Getting to first slider target: {}, {}, {}".format(x, y, self.safe_z_val))
                  arm.move_to(e= x, y= y, z= self.safe_z_val, wait= wait_key)
               else:
                  print ("Getting to first target: {}, {}, {}".format(x, y, self.safe_z_val))
                  arm.move_to(x, y, self.safe_z_val, wait= wait_key)
            
            """
            The rotation does not work for now
            # always rotate to the correct azimuth before touching paper
            # the rotary module is a piece of garbage, not worth it
            # arm.rotate_to(a, wait=wait_key)
            # arm.dealy_s(wait_val)
            """

            # move to the target
            z = self.base_z + p*self.pressure_factor

            if self.slider:
               print ("Getting to the next slider target: {}, {}, {}".format(x, y, z))
               arm.move_to(e= x, y= y, z= z, wait= wait_key)
            else:
               print ("Getting to the next target: {}, {}, {}".format(x, y, z))
               arm.move_to(x= x, y= y, z= z, wait= wait_key)

            arm.dealy_s(wait_val)

         # moves up from paper after the last target
         current_pose = arm.get_current_position()

         if self.slider:
            arm.move_to(e= current_pose[3], y= current_pose[1], z = self.safe_z_val, wait= wait_key)
         else:
            arm.move_to(x= current_pose[0], y = current_pose[1], z= self.safe_z_val, wait= wait_key)


         arm.dealy_s(wait_val)

         print ("<<< polyline {} finished >>> \n".format(i))
      
      print ("<<<<<<<<  Drawing finished  >>>>>>>>")
      arm.go_home()

   def dic_to_json(self, dic_data):
      """
      Converts a dictionary to json format.
      Args: 
         dic_data (dict): data to be converted to JSON

      returns:
         self.json_object (string): dic_data as a string in the json structure
      """
      self.json_string = json.dumps(dic_data, indent = 4) 
      return self.json_object

   def write_dic_to_json_file(self, json_data, path):
      """
      Very quick way to write a json_object to a file

      Args:
         json_data: a serialized json object 
         path (string): where to save the file
      """
      file = open(path, 'w')
      file.write(json_data)
      file.close()

   def json_to_dict(self, json_data= None, json_path=None):
      """
      Converts a json fomat data to a dictionary.
      If given the json_data, it returns the dictionary of it
      If given the json_path, it loads the file, then returns the dictionary
      
      Args: 
         json_data: a serialized json object
         json_path (string): a path that holds the json data as a file, i.e.: "../data/path_data.json"
      
      retunrs:
         dictionary_data (dict): a dictionary holding the data from the JSON file or data
      """

      if json_data is None:
         # in case of no path and no data, 
         # it loads a file from the default path 
         if json_path is None:
            json_path = self.default_path
         raw_data = open(json_path,)
         dictionary_data = json.load(raw_data)
      
      # if given json_data, it always return the dic
      else:
         dictionary_data = json.loads(json_data)

      return dictionary_data
   
   def reset_JSON_file(self, json_path):
      """
      Resets the JSON default file with a boundary drawing
      """      
      drawing_dic = {
                     "drawing": {
                        "strokes": [
                              [
                                 {
                                    "x": 0,
                                    "y": 350,
                                    "a": 0,
                                    "p": 0.0
                                 },
                                 {
                                    "x": 150,
                                    "y": 350,
                                    "a": 0,
                                    "p": 0.0
                                 },
                                 {
                                    "x": 150,
                                    "y": 250,
                                    "a": 0,
                                    "p": 0.0
                                 },
                                 {
                                    "x": 0,
                                    "y": 250,
                                    "a": 0,
                                    "p": 0.0
                                 },
                                 {
                                    "x": 0,
                                    "y": 350,
                                    "a": 0,
                                    "p": 0.0
                                 }
                                 
                              ]
                        ]
                     }
                  }

      json_data = json.dumps(drawing_dic, indent = 4)
      self.write_dic_to_json_file(json_data, json_path)

   def save_json(self, json_data, path=None):
      """
      Writes the json_data to a file
      
      Args: 
         json_data: a serialized json object
         path (string): a path to write the file on, i.e.: "../data/path_data.json"
               if no path given, it writes it on the default path 
      
      returns:
         None
      """

      if path == None:
         path = self.default_path

      with open(path, 'w') as outfile:
            json.dump(json_data, outfile)

   def extract_ploylines(self, json_path= None, data= None):
      """
      Extract all the polylines in a json drawing 
      
      Args: 
         json_path (string): a path to load the file from, i.e.: "./data/path_data.json" 
      
      returns:
         polyLines (nparray): an array of all polylines
      """
      if json_path is None:
         if data is not None:
            print ("reading json data as text")
            print (data)
            drawing_data = self.json_to_dict(json_data = data)
      
      else:
         drawing_data = self.json_to_dict(json_path= json_path)

      strokes = drawing_data['drawing']['strokes']

      polyLines = [pl for pl in strokes]
      polyLines = [self.get_targest_from_polyline(polyLine) for polyLine in polyLines]
      polyLines = np.asarray(polyLines, dtype=object)
      
      return polyLines
         

   def get_targest_from_polyline(self, polyLine):
      """
      Extract all the targest from a given polyline

      Args:
         polyLine (list of dictionaries): the polyline data, i.e.: [{"x": 600, "y": 400, "a": 45, "p": 0.2}, 
                                                    {"x": 600, "y": 300, "a": 45, "p": 0.3}]
      returns:
         point_in_polyline (numpy.ndarray): all the points in the polyline i.e.:
                                                   [[600. 400. 45. 0.2]
                                                    [600. 300. 45. 0.3]]

      """
      point_in_polyline = [np.asarray(list(point.values())) for point in polyLine]
      point_in_polyline = np.asarray(point_in_polyline)
      return point_in_polyline

   


##########################################################################################
###### Dummy Classes
##########################################################################################
class Robot_arm(object):
   """
   A dummy class to work with this file
   """
   def __init__(self):
      pass
   
   def set_module_type(self,module_type):
      if module_type == 6:
         print ("Module set to rotary module")
      else:
         print ("Module is not set to rotary!")
      print ("-----------------------------------------------------")
      print ("\n")
   
   def move_to(self,  x_loc, y_loc, p_val):
      print (("M \t{}\t{}\t{}").format(x_loc, y_loc, p_val))

   def rotate_to(self, r):
      print ("R \t{}".format(r))

   def get_current_position(self):
      x, y, z, e, a, b, c = [0,1,2,3,4,5,6]
      return x, y, z, e, a, b, c

##########################################################################################
###### Test function
##########################################################################################
def test_function():
    arm = Robot_arm()
    dp = Drawing_processor()
    dp.save_json(json_data= raw_data,path= "../data/path_data_test.json")
    polyLines = dp.extract_ploylines("../data/path_data_test.json")
    dp.draw(arm, polyLines)



