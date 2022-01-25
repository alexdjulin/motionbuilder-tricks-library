# Author: Alexandre
## Library of useful functions
####################################

# prerequisites
from pyfbsdk import *
from pyfbsdk_additions import *

# global variables for faster access
lSys = FBSystem()
lScene = lSys.Scene
lApp = FBApplication()
Story = FBStory()

# external libraries
import os
from modules import pyperclip  # for copy to clipboard
from modules import datetime  # for date and time
import file_system_library as flib
import operator
import time

########## COMPONENTS ##########

def unselect_all_comp(log = False):
	''' Unselect all components '''
	
	for comp in lSys.Scene.Components:
		comp.Selected = False
	
	if log:
		print ("All components unselected")

def get_comp_by_name(name, namespace = None, log = False):
	''' Get component by name '''

	if namespace:
		name = "{}:{}".format(namespace, name)
		
	comp = FBFindModelByLabelName(name)
	
	if log:
		print("Returning " + name)

	return comp
	
def select_comp_by_name(name, append = False, log = False):
	''' Selects model by a given name, appends it or not to the selection and returns it '''
	
	if not append:
		unselect_all_comp(log)
	
	model = get_comp_by_name(name, log) 
	model.Selected = True
	
	if log:
		if append:
			print ("Append {}".format(model.Name))
		else:
			print ("Select {}".format(model.Name))

	return model
	
def get_selected_components(log = False):
	''' Returns a list of all selected components from the scene '''
	
	# get the list of selected models
	lModelList = FBModelList()
	FBGetSelectedModels(lModelList)

	if log:
		print ("{} components selected:".format (len (lModelList) ) )
		for element in lModelList:
			print(element.Name)

	return lModelList


def get_selected_components_name(log = False):
	''' Returns name of selected components '''

	comp_names = list()

	for comp in get_selected_components():
		comp_names.append(comp.Name)

	if log:
		print("Selected components: " + ', '.join(comp_names))

	return comp_names

def get_children(parentModel, _childLst = None, includeParent = False, selected = False, log = False):
	''' return the list of all children '''
	
	if not _childLst:
		_childLst = list()

	# Get model children
	children = parentModel.Children
	
	# Check if any children exist
	if (len (children) > 0):
		# Loop through the children
		for child in children:
			# Get any children
			_childLst.append(child)
			get_children(child, _childLst)

	# Select parent
	if includeParent:
		_childLst.append(parentModel)
	
	if log:
		for child in _childLst:
			print child.Namne

	return(_childLst)    

def group_selected_components(log = False):
	''' parent selected components under a new group, name from pop-up'''
	
	# get selected components, check selection
	comp_list = get_selected_components()

	if not comp_list:
		print("Select at least one component to group")
		return

	btn, value = FBMessageBoxGetUserValue( "Group Selected Components", "Enter group name: ", "", FBPopupInputType.kFBPopupString, "Ok", "Cancel")
	
	# if cancel
	if btn == 2:
		return
	
	# default name
	if not value:
		value = "group"
		
	group_parent = comp_list[0].Parent
	
	# create group
	group = FBModelNull(value)
	group.Visibility = True
	group.Size = 0.0
	group.Parent = group_parent

	for comp in comp_list:
		comp.Parent = group
	
	if log:
		print("[{}] parented under {}".format(', '.join(get_selected_components_name()), group.Name))

def delete_selected_components(log = False):
	""" delete all selected components """
	
	lModelList = get_selected_components()
	for model in lModelList:
		print type(model)
		model.FBDelete()

	if log:
		print("Deleting model: {}".format(model.Name))


def delete_model_and_children(pModel, log = False):
	""" delete selected model """

	while len(pModel.Children) > 0:
		delete_model_and_children(pModel.Children[-1])
	pModel.FBDelete()
	if log:
		print("Deleting model: {}".format(pModel.Name))


def get_component_by_namespace(namespace, log = False):
	''' Returns all components sharing a given namespace '''

	lFBList = get_all_scene_components(log)
	lReturnList = []
	for item in lFBList:
		if item.LongName.rsplit(':')[0] == namespace:
			lReturnList.append(item)
	if log:
		print('Returning {} items with namespace {}'.format(len(lReturnList), namespace))
	return lReturnList


def delete_components_from_namespace(namespace, log = False):
	"""" delete all scene components from given namespace """
	""" source: http://www.vicdebaie.com/blog/motionbuilder-python-clean-character-from-scene-with-fbdelete/ """
	
	##Create A List Of All The Scene Eelements We Want To Deal With First
	##Some Of The Order Is Important As To Not Have MoBu Crash
	lFBList = get_all_scene_components(log)
	##Create An Empty List That We Will Store To 
	lRemovelist = []

	##For Every Thing Returned Per Item Within Our lFBList
	for item in lFBList:
		##Look To See If Our "namespace" Provided Exists Within The Items LongName
		if namespace in item.LongName:
			##If Found Store The Item To Our List lRemovelist
			lRemovelist.append(item)
		##If Not Found Skip    
		else: 
			pass
	##Take Every Item We Stored In Our List lRemovelist
	for item in lRemovelist:
		##Delete It
		if log:
			print("Deleting " + item.LongName)
		item.FBDelete()


def get_all_scene_components(log = False):
	""" returns a list of all components in the scene (all types) """
	
	compList = []
	lFBList = [lScene.Constraints, lScene.Handles, lScene.UserObjects, lScene.ControlSets, lScene.CharacterExtensions,lScene.Characters, lScene.Materials, lScene.Shaders, lScene.Textures, lScene.Folders, lScene.ObjectPoses, lScene.CharacterPoses, lScene.KeyingGroups, lScene.Notes, lScene.VideoClips, lScene.Components]##With Each Item In Our List lFBList
	
	for item in lFBList:
		for comp in item:
			compList.append(comp)
			if log:
				print (comp.Name)

	return compList
	
	
def unselect_all_components(log = False):
	""" unselect all scene components """
	
	compList = get_all_scene_components()

	for comp in compList:
		if comp.Selected:
			comp.Selected = False
			if log:
				print("{} unselected".format(comp.Name))

	
def search_components_from_string(string, select = False, log = False):
	""" return a list of all components containing a given string in their name, select them if True """
	
	resultList = []
	unselect_all_components()
	
	for comp in get_all_scene_components():
		if string in comp.Name:
			resultList.append(comp)
			if select and not comp.Selected:
				comp.Selected = True
			if log:
				print comp.Name
	if not resultList:    
		print ("String {} not found in current Scene".format(string))
	   
				
########## JOINTS ##########    

def get_joint_list(log = False):
	""" Get all the children joints from the selected root """

	# Get selected models
	selected_models = FBModelList()
	FBGetSelectedModels(selected_models)

	if len(selected_models) == 0:
		raise ValueError("No joint selected. Please select root joint.")
	elif len(selected_models) > 1:
		raise ValueError("More than one joint selected. Please select root joint only.")
	else:
		joint_list = [joint for joint in get_children(selected_models[0], includeParent = True, log = log) if type(joint) == FBModelSkeleton]
		if log:
			print(joint.Name)

	return joint_list

########## TRANSFORMATIONS ##########

def align_objects(obj, source, log = False):
	
	# Get Our Source's Translation And Rotation
	sourceTrans = FBVector3d()
	sourceRot = FBVector3d()
	source.GetVector (sourceTrans, FBModelTransformationType.kModelTranslation, True)
	source.GetVector (sourceRot, FBModelTransformationType.kModelRotation, True)
	
	# Match Our Object's Translation And Rotation To Match That Of Our Source
	obj.Translation = sourceTrans
	obj.Rotation = sourceRot
	
	if log:
		print "ALIGNING %s to %s" % (obj.Name, source.Name)

########## CONSTRAINTS ##########

def get_constraints():
	# return list of constraints in the scene
	return [const for const in lScene.Constraints]


def get_constraints_name():
	# return list of scene constraints name
	return [const.Name for const in get_constraints()]

def get_constraint_by_name(const_name):
	# return constraint based on its name

	for const in lScene.Constraints:
		if const.Name == "const_name":
			return const

def parentConstraint(parent, child, snap = True, weight = 100, active = True, name = "_parentConst"):
	''' Creates a parent constraint'''
	 
	# get number of available constraints in mobu
	const_nb = FBConstraintManager().TypeGetCount()

	for i in range(const_nb):
		if "Parent/Child" in FBConstraintManager().TypeGetName(i):
			lMyConstraint = FBConstraintManager().TypeCreateConstraint(i)
		 
	lMyConstraint.Name = name
	# assign parent and child
	lMyConstraint.ReferenceAdd (0, child)
	lMyConstraint.ReferenceAdd (1, parent)
	 
	# Snap if user desires
	if snap:
		lMyConstraint.Snap()
	 
	# weight of the constraint
	lMyConstraint.Weight = weight
	 
	# Activate Constraint
	lMyConstraint.Active = active

	return lMyConstraint

def rotationConstraint(parent, child, snap = True, weight = 100, active = True, name = "_rotationConst"):
	''' Creates a rotation constraint'''
	 
	# get number of available constraints in mobu
	const_nb = FBConstraintManager().TypeGetCount()

	for i in range(const_nb):
		if "Rotation" in FBConstraintManager().TypeGetName(i):
			lMyConstraint = FBConstraintManager().TypeCreateConstraint(i)
		 
	lMyConstraint.Name = name
	# assign parent and child
	lMyConstraint.ReferenceAdd (0, child)
	lMyConstraint.ReferenceAdd (1, parent)
	 
	# Snap if user desires
	if snap:
		lMyConstraint.Snap()
	 
	# weight of the constraint
	lMyConstraint.Weight = weight
	 
	# Activate Constraint
	lMyConstraint.Active = active

	return lMyConstraint

########## TAKES ##########

def set_current_take(takeName, log = False):
	''' Set the current take to a given or current one '''
	log_str = None
	
	for take in lSys.Scene.Takes:
		if take.Name == takeName:
			lSys.CurrentTake = take
			log_str = "Current take is {}".format(take.Name)
			break
		else:
			log_str = "ERROR, take {} does not exists".format(takeName)
	 
	if log:
		print (log_str)

def get_take_list(clipboard = None, log = False):
	'''Return the take list from the current scene, copied to clipboard if specified'''

	take_list = []
	# empty clipboard
	if clipboard:
		pyperclip.copy(None)

	for take in lSys.Scene.Takes:
		take_list.append(take.Name)
		if log:
			print (take.Name)
		if clipboard:
			pyperclip.copy(pyperclip.paste() + take.Name + "\n")
		
	if log:
		print ("-------------------------")
		print ("Total: {} takes".format(len(take_list)))
		if clipboard:
			print ("Copied to clipboard")
		
	return take_list
	
def get_take_by_name(takeName = None, log = False):
	'''Return a take by name, current one if not given'''
	
	# if take not specified, current is used
	if not takeName:
		takeName = lSys.CurrentTake.Name
		if log:
			print("Take name not specified.")
	
	# browsing through takes
	for take in lSys.Scene.Takes:
		if take.Name == takeName:
			if log:
				print ("Returning {}".format(takeName))
			return take
	
	# if take not found
	if log:
		print ("ERROR, {} does not exists, returning current take".format(takeName))
		
	return lSys.CurrentTake

def get_current_take(log = False):
	'''Return current take'''

	get_take_by_name(None, log)
	
def get_current_take_name(clipboard = False, log = False):
	'''Return current take name, copied to clipboard if specified'''
		
	takeName = lSys.CurrentTake.Name
	
	if clipboard:
		pyperclip.copy(takeName)
		
	if log:
		print ("Current take is {}".format(takeName))
		if clipboard:
			print("Copied to clipboard")
	
	return takeName
	
def rename_current_take(newTakeName = str(datetime.datetime.now()), log = False):
	'''Rename the current take to a given name, datetime if not specified'''

	lSys.CurrentTake.Name = newTakeName
	
	if log:
		print("Take renamed {}".format(newTakeName))
	 
def create_new_take(takeName = str(datetime.datetime.now()), current = True, log = False):
	''' Create new take with specified name (datetime if not) and set it as current '''

	lSys.Scene.Takes.append(FBTake(takeName))   
	if current:
		set_current_take(takeName, log)
	
	if log:
		print ("New take created: {}".format( takeName))
		
def duplicate_take(takeName = None, newTakeName = str(datetime.datetime.now()), log = False):
	'''Duplicate a take (current if none) with a given name (datetime if none)''' 
	
	if takeName:
		set_current_take(takeName, log)
	
	lSys.CurrentTake.CopyTake(newTakeName)
	
	if log:
		print ("Take {} duplicated and renamed".format(get_current_take_name(log)))
		
	return lSys.CurrentTake.Name

def delete_take_by_name(takeName = lSys.CurrentTake, log = False):
	'''Delete a take by name, current one if not given'''
   
	for take in lSys.Scene.Takes:
		if take.Name == takeName:
			take.FBDelete()
			if log:
				print("Take {} deleted".format(takeName))
			return
	
	# if take does not exist    
	if log:
		print("Take not found, specify a valid take name or none to delete the current one")

def delete_all_takes_but_current(log = False):
	''' Delete all takes but current one '''

	current_take = get_current_take_name()
	for take in get_take_list():
		if take != current_take:
			delete_take_by_name(take)

	if log:
		print("All takes deleted, except {}".format(current_take))

def get_selected_components_name(log = False):
	''' Returns the name of all selected components '''

	lComponents = get_selected_components(log)
	compName = []
	
	for comp in lComponents:
		compName.append(comp.Name)
		if log:
			print (comp.Name)
	
	return compName
	
def plot_to_current_take(log = False):
	''' Plot selected Story clip to the current take '''
	
	selected = 0
	startFrame = None
	endFrame = None
	
	# Toogle Story mode if off
	if Story.Mute:
		toogle_story_mode(log)

	# Frame selected clip
	set_timespan(startFrame, endFrame, log)
	
	# Plot clip to take
	plot_to_skeleton_and_rig(log)
	
	# Log
	if log:
		print ("Story clip plotted to new take {}".format(lSys.CurrentTake.Name))

def plot_to_take(newTake = False, takeName = None, log = False):
	''' Plot selected Story clip to a new take of the name '''
	
	selected = 0
	startFrame = None
	endFrame = None
	
	# Toogle Story mode if off
	if Story.Mute:
		toogle_story_mode(log)
	
	# Get start, end frames and name of selected clips
	for track in Story.RootFolder.Tracks:
		for clip in track.Clips:
			if clip.Selected:
				startFrame = clip.Start.GetFrame()
				endFrame = clip.Stop.GetFrame()
				if newTake and not takeName:
					takeName = clip.Name
				selected += 1    
	
	# Exit function if no clip selected
	if not selected:
		if log:
			print ("ERROR, select (only) one Story clip")
		return
	
	# Get clip name if not given (without extension)
	if not takeName:
		extensions = {".fbx", ".Fbx", ".FBX"}
		for ext in extensions:
			takeName = takeName.replace(ext,"")
	
	# Create new take
	create_new_take(takeName, True, log)
	
	# Frame selected clip
	set_timespan(startFrame, endFrame, log)
	
	# Plot clip to take
	plot_to_skeleton_and_rig(log)
	
	# Log
	if log:
		print ("Story clip plotted to new take {}".format(lSys.CurrentTake.Name))

def go_to_previous_take(loop = True, log = False):
	''' go to previous take, last if reaching the beginning and loop True'''

	take_list = get_take_list()
	take_len = len(take_list)
	
	# get the current take index
	lTakeIdx = take_list.index(lSys.CurrentTake.Name)
			
	# go to the previous take
	if lTakeIdx == 0:
		if loop:
			lTakeIdx = take_len - 1
	else:
		lTakeIdx -= 1
	
	# set the current take
	lSys.CurrentTake = lSys.Scene.Takes[lTakeIdx]
	
	if log:
		print ("Moving to previous take [{}]".format(lSys.CurrentTake.Name))

def go_to_next_take(loop = True, log = False):
	''' go to next take, first if reaching the end and loop True '''

	take_list = get_take_list()
	take_len = len(take_list)
	
	# get the current take index
	lTakeIdx = take_list.index(lSys.CurrentTake.Name)
			
	# go to the previous take
	if lTakeIdx == take_len - 1:
		if loop:
			lTakeIdx = 0
	else:
		lTakeIdx += 1
	
	# set the current take
	lSys.CurrentTake = lSys.Scene.Takes[lTakeIdx]
	
	if log:
		print ("Moving to next take [{}]".format(lSys.CurrentTake.Name))

def add_take_separator(log = False):
	''' Adds separator after the current take '''
	
	# create a unique name
	sep_name = "_" * length(get_current_take_name())
	
	takelist = get_take_list()
	
	while sep_name in takelist:
		sep_name += "_"
	
	create_new_take(sep_name, False, log)
	
	if log:
		print ("Separator added")
		
				
########## TIMELINE ##########

def set_timespan(start, end, log = False):
	''' Set current timespan to start/end frame '''
	
	lSys.CurrentTake.LocalTimeSpan = FBTimeSpan(FBTime(0, 0, 0, start, 0), FBTime(0, 0, 0, end, 0))
	if log:
		print ("TimeSpan set to [{}-{}]".format(start, end))

def get_current_frame(log = False):
	''' get current frane number '''
	
	current = lSys.LocalTime.GetFrame()
	
	if log:
		print ("Current frame is {}".format(current))

	return current
	
def go_to_frame(frame = 0, log = False):
	''' jump to a given frame, 0 as default '''

	t = FBTime(0, 0, 0, frame, 0)
	FBPlayerControl().Goto(t)
	
	if log:
		print ("Go to frame {}".format(t))

	return 0
	
def get_timeline_start_end_frame(log = False):
	''' Returns the start and end frames of the timeline as a tuple '''
	
	lStartFrame = lSys.CurrentTake.LocalTimeSpan.GetStart().GetFrame()
	lEndFrame = lSys.CurrentTake.LocalTimeSpan.GetStop().GetFrame()
	
	if log:
		print ("Timeline frames: [{}-{}]".format(lStartFrame, lEndFrame))
		
	return lStartFrame, lEndFrame

def get_take_length(log = False):
	''' Returns the length in frames of the current take '''
	
	start, end = get_timeline_start_end_frame(log)
	length = end - start

	if log:
		print ("Current take length: {} frames".format(length))

	return length

def set_framerate(fps, log = False):

	modes_dic = {
		'1000': FBTimeMode.kFBTimeMode1000Frames,
		'120': FBTimeMode.kFBTimeMode120Frames,
		'100': FBTimeMode.kFBTimeMode100Frames,
		'96': FBTimeMode.kFBTimeMode96Frames,
		'72': FBTimeMode.kFBTimeMode72Frames,
		'60': FBTimeMode.kFBTimeMode60Frames,
		'59.94': FBTimeMode.kFBTimeMode5994Frames,
		'50': FBTimeMode.kFBTimeMode50Frames,
		'48': FBTimeMode.kFBTimeMode48Frames,
		'30': FBTimeMode.kFBTimeMode30Frames,
		'NTSC_FULL': FBTimeMode.kFBTimeMode30Frames,
		'29.97': FBTimeMode.kFBTimeMode2997Frames,
		'NTSC_DROP': FBTimeMode.kFBTimeMode2997Frames_Drop,
		'25': FBTimeMode.kFBTimeMode25Frames,
		'PAL': FBTimeMode.kFBTimeMode25Frames,
		'24': FBTimeMode.kFBTimeMode24Frames,
		'23.976': FBTimeMode.kFBTimeMode23976Frames,
	}
	
	if str(fps) in modes_dic.keys():
		FBPlayerControl().SetTransportFps(modes_dic[str(fps)])
	else:
		FBPlayerControl().SetTransportFps(FBTimeMode.kFBTimeModeCustom, float(fps))


########## STORY EDITOR ##########

def frame_story_clip(log = False):
	''' Frame selected Story clips by changing the timeline start and end frames '''
	
	nbClips = 0

	for track in FBStory().RootFolder.Tracks:
		for clip in track.Clips:
			if clip.Selected:

				# get selected clip start and end frame
				clipStart = clip.Start.GetFrame()
				clipEnd = clip.Stop.GetFrame()

				# check if first clip has been read or not
				if nbClips == 0:
					startFrame = clipStart
					endFrame = clipEnd
				else:
					# check if clip startframe is inferior to startframe
					if clipStart < startFrame:
						startFrame = clipStart
					if clipEnd > endFrame:
						endFrame = clipEnd
				nbClips += 1

	# set new timeframe if at least one clip selected
	if nbClips > 0:
		set_timespan(startFrame, endFrame)

		# print to log
		if log:
			print ("Framed {} to [{}-{}]]".format(clip.Name, startFrame, endFrame))
	else:
		if log:
			print ("ERROR, select at least one Story Clip")
					
def toogle_story_mode(log = False):
	''' Toggle story mode on/off '''
	
	FBStory().Mute = not FBStory().Mute
	
	if log:
		if FBStory().Mute:
			print ("Story mode OFF")
		else:
			print ("Story mode ON")

def order_takes_based_on_file(filename, log = False):
	'''Reorder the take list based on a text file (one take per line)'''
	
	# Creates list of all takes from file (one element per line)
	textfile = [line.rstrip('\n') for line in open(filename)]
	
	# Create current and new take lists
	takelist = get_take_list()
	new_takelist = []
	
	# Get the id (position) of each take name in the textfile
	take_dict = {}
	takes_not_in_file = 0
	
	for take in takelist:
		if take in textfile:
			take_dict[textfile.index(take)] = take
		else:
			takes_not_in_file += 1
			if log:
				print ("{} not in text file".format(take))
			
	# Sort dict by increasing id
	take_dict = sorted(take_dict.items(), key=operator.itemgetter(0))
	
	# Create separator between takes not in the textfile and the ordered ones
	if takes_not_in_file > 0:
		add_take_separator(log)

	# Duplicates takes in the dict order
	suffix = "___REORDERED___"
	   
	for n in range(len(take_dict)):
		old_name = take_dict[n][-1]
		new_name = old_name + suffix
		duplicate_take(old_name, new_name)
		if log:
			print ("duplicate {}".format(old_name))

	# Update takelist
	takelist = get_take_list()
	
	# Delete old takes (only the ones from the textfile that have been duplicated)
	for takeName in takelist:
		if takeName in textfile:
			get_take(takeName).FBDelete()
			if log:
				print ("delete {}".format(takeName))
	
	# Rename new takes
	for take in lSys.Scene.Takes:
		if suffix in take.Name:
			take.Name = take.Name.replace(suffix, "")
			if log:
				print ("rename {}".format(take.Name))
	
	# print (log)
	if log:
		print ("Takes ordered: {}".format(len(take_dict)))
		print ("Takes not in file: {}".format(takes_not_in_file))

def move_selected_clip_to_frame(frame = get_current_frame(), log = False):
	''' Move a selected clip in the Story Mode to a given frame (current if not specified) '''
	
	if type(frame) != int:
		print ("ERROR, enter frame number as an integer")
		return
		
	for track in Story.RootFolder.Tracks:
		for clip in track.Clips:
			if clip.Selected:
				clip.Start = FBTime(0,0,0,frame)
				if log:
					print ("Clip {} moved to frame {}".format((clip.Name, frame)))

def insert_character_animation_track(log = False):
	''' Insert a character animation track using the current character in the Story Mode and select it '''
	
	track = FBStoryTrack(FBStoryTrackType.kFBStoryTrackCharacter, Story.RootFolder)
	track.Details.append(lApp.CurrentCharacter)
	track.Selected = True
	
	if log:
		print ("Track added to the Story Editor and selected")
		
	return track

def insert_take_in_storyMode(take = lSys.CurrentTake, log = False):
	''' Insert take in Story mode, current if not specified'''
	
	# turn on Story mode
	if Story.Mute:
		toogle_story_mode(log)
	
	# check if existing and selected track
	selected = False
	for track in Story.RootFolder.Tracks:
		if track.Selected:
			selected = True
			
	# if no track or no selected one, creates one and select it
	if not selected:
		newTrack = Story.RootFolder.Tracks.append("Inserted Track") 
		newTrack.Selected = True
		
	# insert current take to selected track
	for track in Story.RootFolder.Tracks:
		if track.Selected:
			inserted_clip = track.CopyTakeIntoTrack(take.LocalTimeSpan, take )
			
			for clip in track.Clips:
				clip.Selected = False
			inserted_clip.Selected = True
			
			if log:
				print ("Take {} inserted in {}".format(take.Name, track.Name))


########## OBJECTS ##########    

def align_objects(source, target, transformation = (0,1,0), log = False):
	''' align source object to target object according to a given transformation tuple (translation, rotation, scale)'''
	
	# Align translation
	if transformation[0]:
		targetTranslation = FBVector3d()
		target.GetVector (targetTranslation, FBModelTransformationType.kModelTranslation, True)
		source.Translation = targetTranslation
		
	# Align rotation
	if transformation[1]:
		targetRotation = FBVector3d()
		target.GetVector (targetRotation, FBModelTransformationType.kModelRotation, True)
		source.Rotation = targetRotation

	# Align scale
	if transformation[2]:
		targetScale = FBVector3d()
		target.GetVector (targetScale, FBModelTransformationType.kModelScaling, True)
		source.Scaling = targetScale
	
	if log:
		print ("{} aligned to {}".format(source.Name, target.Name))
		
def align_objects_from_name(source_name, target_name, transformation = (1,1,0), log = False):
	''' align a source object to a target one based on a string name input '''
	
	source = get_comp_by_name(source_name)
	target = get_comp_by_name(target_name)
	align_objects(source, target, transformation, log)


########## KEYS ##########

def set_key(log = False):
	''' set key on selected at current time '''
	
	FBPlayerControl().Key()
	if log:
		print("Key added at current time")

def clear_anim(pNode, log = False):
	''' clear all keys on passed animation node '''
	
	# check if keys on selecte model
	if pNode.FCurve:
		pNode.FCurve.EditClear()
	
	# if not, browse recursively through children until finding a model with keys
	else:
		for lNode in pNode.Nodes:
			clear_anim( lNode )

def clear_anim_on_selected(log = False):
	''' clear all keys on selected objects (current layer) '''

	# get list of selected models
	lModels = FBModelList()
	FBGetSelectedModels( lModels )

	# clear animation on selected
	for lModel in lModels:
		clear_anim( lModel.AnimationNode, log )
		if log:
			print( "Anim keys deleted on {}".format(lModel.Name))


########## CHARACTERS ##########       

def set_current_character(character, log = False):
	''' set the current character '''

	lApp.CurrentCharacter = character

	if log:
		print("Current character is " + character.Name)


def set_current_character_by_name(name, log = False):
	''' set the current character based on string '''
	
	char_exists = False
	lCharInScene = lScene.Characters
	for character in lCharInScene:

			if character.Name == name:
				set_current_character(character)
				char_exists = True
			   
	if log:
		 if char_exists:
			 print("Current character is " + name)
		 else:
			 print(name + " is not a scene character")
 
	return lApp.CurrentCharacter
	 
	 
def get_character_by_name(name, log = False):
	''' get a character based on string '''
	
	lCharInScene = lScene.Characters
	for character in lCharInScene:
		if character.Name == name:
			if log:
				print("Returning " + name)
			return character
	
	if log:
		print("ERROR, {} does not exist".format(name))
		
		
def plot_to_skeleton(char = lApp.CurrentCharacter, log = False):
	''' Plot a character (current if not specified) motion onto the skeleton '''

	# Defining the Plot option that will be used        
	PlotOptions = FBPlotOptions()
	PlotOptions.ConstantKeyReducerKeepOneKey = False
	PlotOptions.PlotAllTakes = False
	PlotOptions.PlotOnFrame = True
	PlotOptions.PlotPeriod = FBTime( 0, 0, 0, 1 )
	PlotOptions.PlotTranslationOnRootOnly = False
	PlotOptions.PreciseTimeDiscontinuities = False
	PlotOptions.RotationFilterToApply = FBRotationFilter.kFBRotationFilterUnroll
	PlotOptions.UseConstantKeyReducer = False
	 
	# Plotting to the skeleton
	char.PlotAnimation(FBCharacterPlotWhere.kFBCharacterPlotOnSkeleton,PlotOptions)

	if log:
		print ("{} motion plotted on skeleton".format(char.Name))

def plot_to_rig(char = lApp.CurrentCharacter, log = False):
	''' Plot a character (current if not specified) motion onto the rig '''
	
	# Defining the Plot option that will be used        
	PlotOptions = FBPlotOptions()
	PlotOptions.ConstantKeyReducerKeepOneKey = False
	PlotOptions.PlotAllTakes = False
	PlotOptions.PlotOnFrame = True
	PlotOptions.PlotPeriod = FBTime( 0, 0, 0, 1 )
	PlotOptions.PlotTranslationOnRootOnly = False
	PlotOptions.PreciseTimeDiscontinuities = False
	PlotOptions.RotationFilterToApply = FBRotationFilter.kFBRotationFilterUnroll
	PlotOptions.UseConstantKeyReducer = False
	
	# Plotting to the rig
	char.PlotAnimation(FBCharacterPlotWhere.kFBCharacterPlotOnControlRig,PlotOptions)

	if log:
		print ("{} motion plotted on rig".format(char.Name))
		
def plot_to_skeleton_and_rig(log = False):
	'''Plot to skeleton and back to rig'''

	char = lApp.CurrentCharacter
	plot_to_skeleton(char, log)
	plot_to_rig(char, log)


def plot_selected_all_properties(log = False):
	
	# Set options for Plot process
	lOptions = FBPlotOptions()   
	lOptions.ConstantKeyReducerKeepOneKey = False
	lOptions.PlotAllTakes = False
	lOptions.PlotOnFrame = True
	lOptions.PlotPeriod = FBTime( 0, 0, 0, 1 )
	lOptions.PlotTranslationOnRootOnly = False
	lOptions.PreciseTimeDiscontinuities = True
	lOptions.RotationFilterToApply = FBRotationFilter.kFBRotationFilterGimbleKiller
	lOptions.UseConstantKeyReducer = False
	
	lSys.CurrentTake.PlotTakeOnSelected(lOptions)

	if log:
		print("Selected components plotted (all properties")

def characterise_skeleton(skeleton_name, system = 'OT', log = False):

	if system == 'OT':
		# handle optitrack exported skeleton
		char_prefix = skeleton_name + "_"
		root_joint_name = char_prefix + "Hips"
		root_joint = get_comp_by_name(root_joint_name)
		root_joint_height = root_joint.Translation[1]
		
		# go to frame -1
		go_to_frame(-1, log)

		# zero out the root translation at hips_height
		root_joint.Translation = FBVector3d(0,root_joint_height,0)

		# zero out rotation on all joints
		children = get_children(root_joint)
		for child in children:
			child.Rotation = FBVector3d(0,0,0)

		# key skeleton
		set_key(log)

	elif system == 'XS':
		char_prefix = ''
		root_joint_name = "Hips"
		go_to_frame(-1, log)

	else:
		raise ValueError("system argument must be of type string and value OT (OptiTrack) or XS (Xsens)")


	# create a new character
	pCharacter = FBCharacter(skeleton_name)
	FBApplication().CurrentCharacter = pCharacter

	# Select root joint and joint hierarchy
	select_comp_by_name(root_joint_name)
	joints = get_joint_list(log)

	# Assign joints using the HIK template
	fails = list()
	for joint in joints:
		slot = pCharacter.PropertyList.Find(joint.Name.replace(char_prefix, "") + 'Link')  # todo: This only works for HIK naming convention. Prompt for preset?
		if slot is not None:
			slot.append(joint)
		else:
			fails.append(joint.Name)
	
	# Flag that the character has been characterized
	pCharacter.SetCharacterizeOn(True)
	unselect_all_comp(log)

	if log:
		print(skeleton_name + " characterised")


########## IMPORT/EXPORT ##########     
def export_character_animation(target_path, rig_name, lSaveOptions = False, log = False):
	''' Export character animation using given or default options '''

	# Default Save Animation Options    
	if not lSaveOptions:
		lSaveOptions = FBFbxOptions (False) # false = will not save options 
		lSaveOptions.SaveCharacter = True
		lSaveOptions.SaveControlSet = False
		lSaveOptions.SaveCharacterExtention = False
		lSaveOptions.ShowFileDialog = False
		lSaveOptions.ShowOptionslDialog = False

	target_dir = os.path.dirname(target_path)
	flib.ensure_dir(target_dir)
	rig_char = get_character_by_name(rig_name)
	
	lApp.SaveCharacterRigAndAnimation(target_path, rig_char, lSaveOptions)

	if log:
		print("{} has been exported here: {}".format(rig_name, target_path))


########## HUDS ##########   

def add_text_hud_to_camera(HUD_name = "HUD", camera_name = "Perspective", text_element = "TextHUD", text_content = "myText", text_font = "Arial", text_height = 5, text_justif = FBHUDElementHAlignment.kFBHUDLeft, text_dock_horizontal = FBHUDElementHAlignment.kFBHUDLeft, text_dock_vertical = FBHUDElementVAlignment.kFBHUDTop):
	''' Add a text HUD to a given camera (default top-left) '''

	HUD = FBHUD(HUD_name)
	lText = FBHUDTextElement(text_element)
	lScene.ConnectSrc(HUD)          #Connect the HUD to the scene
	lText.Content =  text_content
	lText.Font = text_font   
	lText.Height = text_height
	lText.Justification = text_justif 
	lText.HorizontalDock = text_dock_horizontal
	lText.VerticalDock = text_dock_vertical
	HUD.ConnectSrc(lText) #Connect HUDTextElement to the HUD
	get_comp_by_name(camera_name).ConnectSrc(HUD)

########## MISC ##########

def build_review(log = False):  
	''' Puts all takes one after the other in the Story editor for reviewing  '''          
	
	# Get take list
	take_list = get_take_list()
	
	# Toogle Story mode on and create new character track
	Story.Mute = False
	track = insert_character_animation_track()
	
	frame = 0
	count = 0
	
	# Fill up Story track for all valid takes 
	for take in take_list:
		if take[0] != "_":
			if log:
				print ("Inserting {}".format(take))
			set_current_take(take)
			insert_current_take()
			length = get_take_length()
			move_selected_clip_to_frame(frame)  
			frame += length
			count += 1
	
	create_new_take("___REVIEW___")
	set_timespan(0,frame)
	
	if log:
		print ("{} takes inserted in the Story Editor".format(count))
		
		
############ TEST AREA ###############