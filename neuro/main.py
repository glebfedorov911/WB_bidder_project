from moviepy import VideoFileClip

# Имя файла
input_file = "PyTorch for Deep Learning & Machine Learning – Full Course.mp4"  # Замените на имя вашего файла
output_folder = "./"  # Папка, куда сохранять части

# Загрузка видео
video = VideoFileClip(input_file)

# Длина видео в секундах
duration = video.duration

# Вычисление длины одной части
part_duration = duration / 24

# Разделение видео на части
for i in range(19,25):
    start_time = i * part_duration
    end_time = start_time + part_duration

    # Создание части
    video_part = video.subclipped(start_time, end_time)

    # Сохранение части
    output_file = f"{output_folder}part_{i + 1}.mp4"
    video_part.write_videofile(output_file, codec="libx264")

print("Видео успешно разделено на 24 части!")