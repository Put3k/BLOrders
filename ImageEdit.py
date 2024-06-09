from PIL import Image
from datetime import datetime
import tempfile
import os

def scale_image(image, target_height, max_scale_factor):
    original_width, original_height = image.size

    # Oblicz maksymalny dopuszczalny rozmiar szerokości na podstawie proporcji wysokości 30 cm
    max_width = original_width * (target_height / original_height)

    # Oblicz nową wysokość i szerokość obrazu z uwzględnieniem maksymalnego współczynnika skalowania
    new_height = target_height
    new_width = min(original_width * max_scale_factor, max_width)

    # Sprawdź, czy nowe wymiary przekraczają oryginalne
    if new_height > original_height or new_width > original_width:
        # Powiększ obraz, zachowując proporcje
        image.thumbnail((new_width, new_height))
        return image
    else:
        return None



def scale_for_kid_size(image: Image, max_width_cm: int, max_height_cm: int) -> Image:
    '''
    Scale image to 25x20 max size.
    '''
    max_width_px = int((max_width_cm * 37.8) / 0.48)
    max_height_px = int((max_height_cm * 37.8) / 0.48)

    image.thumbnail((max_width_px, max_height_px))

    return image



def merge_images(images, output_path, target_height_cm=30, spacing_cm=1):

    target_height = int((target_height_cm * 37.8)/0.48)
    spacing = int((spacing_cm * 37.8)/0.48)

    total_images = len(images)
    total_spacing = (total_images - 1) * spacing

    total_width = 0

    image_heights = []
    rotated_images = []

    list_of_images = []

    for image_path in images:
        file_name = image_path.split("/")[-1]
        image = Image.open(image_path)
        image_width, image_height = image.size

        if image_width > image_height:
            image = image.rotate(90, expand=True)
            image_width, image_height = image.size

        if image_height > target_height:
            image.thumbnail([target_height, target_height])
            image_width, image_height = image.size
            total_width += image_width
            list_of_images.append(image)

        elif image_height < target_height:
            bigger_image = scale_image(image, target_height, 1.3)
            if bigger_image:
                image_width, image_height = bigger_image.size
                total_width += image_width
                list_of_images.append(bigger_image)
            else:
                print(f"Plik {file_name} jest zbyt mały aby go powiększyć.")

        else:
            list_of_images.append(image)


    total_width += total_spacing

    merged_image = Image.new('RGBA', (int(total_width), int(target_height)), (0, 0, 0, 0))

    x_offset = 0
    for image in list_of_images:
        image_width, image_height = image.size

        merged_image.paste(image, (int(x_offset), 0), mask=image)

        x_offset += image_width + spacing

    merged_image.save(output_path, dpi=(200, 200))


def split_list(list, size=6):
    return [list[i:i+size] for i in range(0, len(list), size)]

#Na podstawie wskazanej ścieżki, tworzy listę list plików png dzieląc je na chunki (6 plików)
def list_files_as_chunk(folder_path):

    list_of_files = os.listdir(folder_path)
    images_list = []

    for i, f in enumerate(list_of_files):
        if f.endswith(".png"):
            full_path = os.path.join(folder_path, f)
            images_list.append(full_path)

    chunk_list = split_list(images_list)
    return chunk_list


def merge(origin_folder, destination_folder):
    target_height = 30  # 30 cm w dpi (37.8 piksela/cm)
    spacing = 1  # Odstęp między obrazami w cm

    chunk_list = list_files_as_chunk(origin_folder)
    designs_count = 0

    dt_string = datetime.now().strftime("%d-%m-%Y - %H%M%S")

    for i, chunk in enumerate(chunk_list):
        designs_count += len(chunk)
        save_folder = os.path.join(destination_folder, f"{i+1}__{dt_string}.png")
        merge_images(chunk, save_folder, target_height, spacing)

    return designs_count
