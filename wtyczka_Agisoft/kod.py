import Metashape
import os
from PyQt6.QtWidgets import *

app: Metashape.Application = Metashape.Application()
doc: Metashape.Document = app.document

compatible_major_version = "2.1"
found_major_version = ".".join(Metashape.app.version.split('.')[:2])
if found_major_version != compatible_major_version:
    raise Exception("Incompatible Metashape version: {} != {}".format(found_major_version, compatible_major_version))

def find_files(folder, types):
    return [entry.path for entry in os.scandir(folder) if (entry.is_file() and os.path.splitext(entry.name)[1].lower() in types)]

def transform_markers(chunk, source_crs, target_crs):

    for marker in chunk.markers:
        if marker.reference.location: 
            original_location = marker.reference.location
            transformed_location = Metashape.CoordinateSystem.transform(
                original_location, source_crs, target_crs
            )
            marker.reference.location = transformed_location

def get_photos(generate_dense_point_cloud, generate_model, save, downscale1):
    selected_crs = app.getCoordinateSystem()
    chunk = doc.chunk
    if chunk: 
        doc.remove(chunk)
        chunk = None
    # if not chunk:
    chunk = doc.addChunk()
    photo_folder = app.getExistingDirectory("Please select the folder of photos to load.")
    if not photo_folder:
        return
    
    image_types = [".jpg", ".jpeg"]
    photos = find_files(photo_folder, image_types)
    chunk.addPhotos(photos)

    chunk.crs = Metashape.CoordinateSystem("EPSG::2178")  
    chunk.camera_crs = Metashape.CoordinateSystem("EPSG::4326")  
    chunk.marker_crs = selected_crs

    chunk.crs = selected_crs
    chunk.updateTransform()

    source_crs_markers = Metashape.CoordinateSystem("EPSG::2178")

    with open(r"C:\Sem5\fotka\projekt1\osnowa_UAV.txt") as file:
        for line in file:
            name, y, x, z = line.split()
            y, x, z = float(y), float(x), float(z) - 31.13 
            marker = chunk.addMarker()
            marker.reference.location = Metashape.Vector([x, y, z])

    transform_markers(chunk, source_crs_markers, selected_crs)

    chunk.matchPhotos(downscale=downscale1, generic_preselection=True, reference_preselection=True)
    chunk.alignCameras()

    if generate_dense_point_cloud:
        chunk.buildDepthMaps()
        chunk.buildPointCloud()
    
    if generate_model:
        chunk.buildModel()

    if save: # w wersji demo zapis jest nie możliwy
        output_folder = photo_folder 
        model_path = os.path.join(output_folder, "model.obj")  
        point_cloud_path = os.path.join(output_folder, "point_cloud.las")  
        chunk.exportPointCloud(point_cloud_path) 
        chunk.exportModel(model_path)
        output_file = os.path.join(photo_folder, "output_project.psx")
        doc.save(output_file)
    
def wizard():
    qt_app = QApplication.instance()  
    if not qt_app:  
        qt_app = QApplication([])
    window = QWidget()
    layout = QVBoxLayout()

    title_label = QLabel("Agisoft Metashape Pro")
    layout.addWidget(title_label)

    btn_get_photos = QPushButton("Run Wizard")

    generate_dense_point_cloud_checkbox = QCheckBox("Generate Dense Point Cloud")
    layout.addWidget(generate_dense_point_cloud_checkbox)
    generate_dense_point_cloud_checkbox.setChecked(True)  

    generate_3d_model_checkbox = QCheckBox("Generate 3D Model (Mesh)")
    layout.addWidget(generate_3d_model_checkbox)
    generate_3d_model_checkbox.setChecked(True)  

    save_checkbox = QCheckBox("Save")
    layout.addWidget(save_checkbox)
    save_checkbox.setChecked(False)  

    downscale_label = QLabel("Select Downscale Level:")
    layout.addWidget(downscale_label)

    downscale_combobox = QComboBox()
    downscale_combobox.addItems(["16 (Lowest Quality)", "8 (Low Quality)", "4 (Medium Quality)", "2 (High Quality)", "1 (Highest Quality)"])
    layout.addWidget(downscale_combobox)

    def on_get_photos_button_clicked():
        generate_dense_point_cloud = generate_dense_point_cloud_checkbox.isChecked()
        generate_model = generate_3d_model_checkbox.isChecked()
        save = save_checkbox.isChecked()

        downscale_text = downscale_combobox.currentText()
        downscale1 = int(downscale_text.split()[0]) 

        get_photos(generate_dense_point_cloud, generate_model, save, downscale1)

    btn_get_photos.clicked.connect(on_get_photos_button_clicked)
    layout.addWidget(btn_get_photos)
    window.setLayout(layout)
    window.show()
    qt_app.exec()

app.removeMenuItem("Wizard")
app.addMenuItem("Wizard", wizard)


