import math
import ui
import json
import numpy as np
import matplotlib.pyplot as plt

recipe_mode_keys = "Flour Water Salt Starter".split()
experiment_mode_keys = ["Dough Weight", "Water to Flour Ratio", "Salt to Flour Ratio", "Starter to Flour Ratio"]
saved_data_file = "proving_time_saved_data.json"

#saved_data_dict = {"Flour":400,
#"Water":325,
#"Salt":10,
#"Starter":200,
#"Temperature":19,
#"Dough Weight":700,
#"Water to Flour Ratio":0.75,
#"Salt to Flour Ratio":0.02,
#"Starter to Flour Ratio":0.15}

#with open(saved_data_file, 'w') as out_file:
#    json.dump(saved_data_dict, out_file)

with open(saved_data_file) as in_file:
    saved_data_dict = json.load(in_file)

recipe_mode_data = {}
experiment_mode_data = {}
for key, value in saved_data_dict.items():
    if key in recipe_mode_keys:
        recipe_mode_data[key] = value
    if key in experiment_mode_keys:
        experiment_mode_data[key] = value


def proportions_from_recipe(flour, water, salt, starter):
    dough_weight = flour + water + starter
    water_to_flour_ratio = (water + (starter / 2)) / (flour + (starter / 2) + salt)
    salt_to_flour_ratio = salt / (flour + (starter / 2))
    starter_to_flour_ratio = starter / (flour + (starter / 2))

    return (
        dough_weight,
        water_to_flour_ratio,
        salt_to_flour_ratio,
        starter_to_flour_ratio,
    )


def quantity_calculations(
    dough_weight, water_to_flour_ratio, salt_to_flour_ratio, starter_to_flour_ratio
):
    total_flour = dough_weight / (1 + water_to_flour_ratio + salt_to_flour_ratio)
    total_starter = total_flour * starter_to_flour_ratio
    total_salt = total_flour * salt_to_flour_ratio

    starter_flour = total_starter / 2
    starter_water = total_starter / 2

    flour = total_flour - starter_flour
    water = (total_flour * water_to_flour_ratio) - starter_water

    return (
        total_flour,
        total_starter,
        total_salt,
        starter_flour,
        starter_water,
        flour,
        water,
    )


def proving_time(proving_temperature, starter_to_flour_ratio):

    temperature_in_f = (proving_temperature * (9 / 5)) + 32

    # Coefficients
    ln = 0.894
    forth = -0.0000336713
    cubed = 0.0105207916
    squared = -1.2495985607
    single = 67.0024722564
    const = -1374.654056564

    # Calculation of proving time
    proving_time = (math.log(starter_to_flour_ratio / ln)) * (
        (forth * temperature_in_f ** 4)
        + (cubed * temperature_in_f ** 3)
        + (squared * temperature_in_f ** 2)
        + (single * temperature_in_f)
        + (const)
    )

    hours = math.floor(proving_time)
    minutes = (proving_time % 1) * 60

    return (hours, minutes, proving_time)


def save_out_data(list_of_keys, calc_settings, proving_temperature):
    for i, item in enumerate(list_of_keys):
        saved_data_dict[item] = calc_settings[i]
        saved_data_dict["Temperature"] = proving_temperature
    with open(saved_data_file, 'w') as out_file:
        json.dump(saved_data_dict, out_file)


def read_slider(sender):
    slider_value = sender.value
    temperature_min = 18
    temperature_max = 24
    temperature_difference = temperature_max-temperature_min
    temperature_to_set = round((temperature_min + (slider_value*temperature_difference))*2)/2
    proving_temperature = float(temperature_to_set)
    sender.superview["prove_temp_field"].text = str(proving_temperature)
    if sender.superview["segment_control"].selected_index == 0:
        calc_recipe_mode(sender.superview)
    else:
        calc_experiment_mode(sender.superview)


def calc_recipe_mode(sender):
    flour = int(v["field_1"].text)
    water = int(v["field_2"].text)
    salt = int(v["field_3"].text)
    starter = int(v["field_4"].text)
    proving_temperature = float(v["prove_temp_field"].text)
    calc_settings = [flour, water, salt, starter]

    (
        dough_weight,
        water_to_flour_ratio,
        salt_to_flour_ratio,
        starter_to_flour_ratio,
    ) = proportions_from_recipe(flour, water, salt, starter)
    (
        total_flour,
        total_starter,
        total_salt,
        starter_flour,
        starter_water,
        flour,
        water,
    ) = quantity_calculations(
        dough_weight, water_to_flour_ratio, salt_to_flour_ratio, starter_to_flour_ratio
    )
    hours, minutes, prove_t = proving_time(proving_temperature, starter_to_flour_ratio)

    v[
        "results_field"
    ].text = f"Dough Weight: {dough_weight:.0f}\nTotal Flour: {total_flour:.0f}\nWater To Flour Ratio: {water_to_flour_ratio:.2f}\nSalt To Flour Ratio: {salt_to_flour_ratio:.2f}\nStarter To Flour Ratio: {starter_to_flour_ratio:.2f}\n\nProving Time: {hours:.0f} hours {minutes:.0f} minutes"
    save_out_data(recipe_mode_keys, calc_settings, proving_temperature)
    return starter_to_flour_ratio
    


def calc_experiment_mode(sender):
    dough_weight = int(v["field_1"].text)
    water_to_flour_ratio = float(v["field_2"].text)
    salt_to_flour_ratio = float(v["field_3"].text)
    starter_to_flour_ratio = float(v["field_4"].text)
    proving_temperature = float(v["prove_temp_field"].text)
    calc_settings = [dough_weight, water_to_flour_ratio, salt_to_flour_ratio, starter_to_flour_ratio]

    (
        total_flour,
        total_starter,
        total_salt,
        starter_flour,
        starter_water,
        flour,
        water,
    ) = quantity_calculations(
        dough_weight, water_to_flour_ratio, salt_to_flour_ratio, starter_to_flour_ratio
    )
    hours, minutes, prove_t = proving_time(proving_temperature, starter_to_flour_ratio)

    v[
        "results_field"
    ].text = f"Flour: {flour:.0f}\nWater: {water:.0f}\nSalt: {total_salt:.0f}\nStarter: {total_starter:.0f}\nTotal Flour: {total_flour:.0f}\n\nProving Time: {hours:.0f} hours {minutes:.0f} minutes"
    save_out_data(experiment_mode_keys, calc_settings, proving_temperature)


def setup_recipe_mode(sender):
    for i, (key, value) in enumerate(recipe_mode_data.items()):
        sender[f"label_{i+1}"].text = key
        sender[f"field_{i+1}"].text = str(value)
    for i in range(4):
        sender[f"field_{i+1}"].action = calc_recipe_mode
    sender["prove_temp_field"].action = calc_recipe_mode
    sender[
        "results_field"
    ].text = "Dough Weight:\nTotal Flour:\nWater To Flour Ratio:\nSalt To Flour Ratio:\nStarter To Flour Ratio:\n\nProving Time:"
    calc_recipe_mode(sender)


def setup_experiment_mode(sender):
    for i, (key, value) in enumerate(experiment_mode_data.items()):
        sender[f"label_{i+1}"].text = key
        sender[f"field_{i+1}"].text = str(value)
    for i in range(4):
        sender[f"field_{i+1}"].action = calc_experiment_mode
    v["prove_temp_field"].action = calc_experiment_mode
    sender[
        "results_field"
    ].text = "Flour:\nWater:\nSalt:\n Starter:\nTotal Flour:\n\nProving Time:"
    calc_experiment_mode(sender)


def setup_segment_control(sender):
    selection = sender.selected_index
    if selection == 1:
        setup_experiment_mode(sender.superview)
    else:
        setup_recipe_mode(sender.superview)
        
        
def plot_temp_dependency(sender):
    temp = np.linspace(18, 24, 10)
    if sender.superview["segment_control"].selected_index == 1:
        s_r = float(sender.superview["field_4"].text)
    else:
        s_r = calc_recipe_mode(sender.superview)
    time = []
    for t in temp:
        hours, minutes, prove_t = proving_time(t, s_r)
        time.append(prove_t)
    
    fig, ax = plt.subplots()
    ax.grid(True)
    ax.plot(temp, time, "-o")
    plt.title(f"Proving Time vs Temperature at {s_r:.2f} Starter Ratio")
    plt.xlabel("Temperature [C]")
    plt.ylabel("Proving Time [Hours]")
    plt.show()


def plot_starter_dependency(sender):
    starter_ratio = np.linspace(0.05, 0.5, 10)
    temp = float(sender.superview["prove_temp_field"].text)
    time = []
    for r in starter_ratio:
        hours, minutes, prove_t = proving_time(temp, r)
        time.append(prove_t)

    fig, ax = plt.subplots()
    ax.grid(True)
    ax.plot(starter_ratio, time, "-o")
    plt.title(f"Proving Time vs Starter Ratio at {temp}C")
    plt.xlabel("Starter Ratio [%]")
    plt.ylabel("Proving Time [Hours]")
    plt.show()
        
        
frame_width = 375
frame_height = 812
margin = 25
frame_width_no_margin = frame_width-(2*margin)
frame_height_no_margin = frame_height-(2*margin)
frame_x_zero = margin
default_control_height = 40
default_padding = 60

v = ui.View()
v.name = "Proving Time"
v.background_color = "white"
v.frame = (0, 0, frame_width, frame_height)

segment_control = ui.SegmentedControl()
segment_control.name = "segment_control"
segment_control.segments = ["Recipe", "Experiment"]
segment_control.width = frame_width_no_margin-(2*margin)
segment_control.height = default_control_height
segment_control.center = (v.width*0.5, default_padding-20)
segment_control.selected_index = 0
segment_control.action = setup_segment_control

for i in range(4):
    label_instance = ui.Label()
    label_instance.name = "label_" + str(i+1)
    label_instance.alignment = ui.ALIGN_RIGHT
    label_instance.width = (frame_width-3*margin)/2
    label_instance.height = default_control_height
    label_instance.center = (0.25*frame_width+margin/4, 110+i*default_padding)
    label_instance.font = ("<system>", 14)
    v.add_subview(label_instance)
    
for i in range(4):
    field_instance = ui.TextField()
    field_instance.name = "field_" + str(i+1)
    field_instance.width = (frame_width-3*margin)/2
    field_instance.height = default_control_height
    field_instance.center = (0.75*frame_width-margin/4, 110+i*default_padding)
    field_instance.font = ("<system>", 14)
    v.add_subview(field_instance)

prove_temp_label = ui.Label()
prove_temp_label.name = "prove_temp_label"
prove_temp_label.alignment = ui.ALIGN_RIGHT
prove_temp_label.width = (frame_width-3*margin)/2
prove_temp_label.height = default_control_height
prove_temp_label.center = (0.25*frame_width+margin/4, 110+4*default_padding)
prove_temp_label.font = ("<system>", 14)
prove_temp_label.text = "Temperature"

prove_temp_field = ui.TextField()
prove_temp_field.name = "prove_temp_field"
prove_temp_field.width = (frame_width-3*margin)/2
prove_temp_field.height = default_control_height
prove_temp_field.center = (0.75*frame_width-margin/4, 110+4*default_padding)
prove_temp_field.font = ("<system>", 14)
prove_temp_field.text = str(saved_data_dict["Temperature"])

prove_temp_slider = ui.Slider()
prove_temp_slider.name = "prove_temp_slider"
prove_temp_slider.width = (frame_width-3*margin)/2
prove_temp_slider.height = default_control_height
prove_temp_slider.center = (0.75*frame_width-margin/4, 110+4*default_padding+25)
prove_temp_slider.action = read_slider

results_field_y_start = 6*default_padding-20+10+default_control_height+10

results_field = ui.TextView()
results_field.name = "results_field"
results_field.background_color = "#eeeeee"
results_field.alignment = ui.ALIGN_LEFT
results_field.corner_radius = 10
results_field.font = ("<system>", 14)
results_field.frame = (margin, results_field_y_start, frame_width_no_margin, 135)

temp_dependency = ui.Button()
temp_dependency.name = "temp_dependency"
temp_dependency.title = "Plot Temperature"
temp_dependency.width = (frame_width-3*margin)/2
temp_dependency.height = default_control_height
temp_dependency.center = (0.25*frame_width+margin/4, 580)
temp_dependency.font = ("<system>", 14)
temp_dependency.background_color = "#3564bd"
temp_dependency.tint_color = "white"
temp_dependency.corner_radius = 10
temp_dependency.action = plot_temp_dependency

starter_dependency = ui.Button()
starter_dependency.name = "starter_dependency"
starter_dependency.title = "Plot Starter"
starter_dependency.width = (frame_width-3*margin)/2
starter_dependency.height = default_control_height
starter_dependency.center = (0.75*frame_width-margin/4, 580)
starter_dependency.font = ("<system>", 14)
starter_dependency.background_color = "#288f31"
starter_dependency.tint_color = "white"
starter_dependency.corner_radius = 10
starter_dependency.action = plot_starter_dependency

controls_list = [segment_control, prove_temp_label, prove_temp_field, results_field, prove_temp_slider, temp_dependency, starter_dependency]
[v.add_subview(item) for item in controls_list]

setup_recipe_mode(v)
v.present("sheet")

