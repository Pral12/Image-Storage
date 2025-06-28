// Получаем все изображения
const images = document.querySelectorAll('.cat-image');

// Индекс текущего изображения
let currentIndex = 0;

// Функция для показа следующего изображения
function showNextImage() {
  // Скрываем текущее изображение
  images[currentIndex].classList.remove('active');

  // Увеличиваем индекс на 1
  currentIndex = (currentIndex + 1) % images.length;

  // Показываем следующее изображение
  images[currentIndex].classList.add('active');
}

// Автоматически переключаем изображения каждые 3 секунды
setInterval(showNextImage, 3000); // 3000 мс = 3 секунды

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-file-btn');
    const uploadStatus = document.getElementById('upload-status');
    const uploadMessage = document.getElementById('upload-message');
    const imageUrlInput = document.getElementById('image-url');
    const copyBtn = document.getElementById('copy-btn');

    // Открыть диалог выбора файла при клике на кнопку
    browseBtn.addEventListener('click', () => {
        fileInput.click();
    });

    // Обработка события изменения input file
    fileInput.addEventListener('change', async () => {
        const file = fileInput.files[0];

        if (!file) return;

        // Проверка формата файла
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg'];
        if (!allowedTypes.includes(file.type)) {
            showUploadError('Не правильный тип файла. Поддерживаются только .jpg, .jpeg, .png и .gif.');
            return;
        }

        // Проверка размера файла
        if (file.size > 5 * 1024 * 1024) { // 5MB
            showUploadError('Размер файла превышает лимит в 5 МБ');
            return;
        }

        // Отправить файл на сервер
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.json(); // Получаем JSON
                imageUrlInput.value = data.url;
                showUploadSuccess();
            } else {
                const errorData = await response.json();
                showUploadError(errorData.detail || 'Загрузка не удалась');
            }
        } catch (error) {
            console.error('Ошибка загрузки файла: ', error);
            showUploadError('Произошла ошибка при загрузке. Попробуйте еще раз.');
        }
    });

    // Копирование URL
    copyBtn.addEventListener('click', () => {
        const url = imageUrlInput.value;
        if (url) {
            navigator.clipboard.writeText(url).then(() => {
                alert('URL-адрес скопирован в буфер обмена!');
            }).catch((err) => {
                console.error('Не удалось скопировать: ', err);
            });
        }
    });

    // Функция показа ошибки
    function showUploadError(message) {
        uploadStatus.textContent = 'Загрузка не удалась';
        uploadMessage.textContent = message;
        uploadStatus.style.display = 'block';
        uploadMessage.style.color = 'red';
    }

    // Функция показа успешной загрузки
    function showUploadSuccess() {
        uploadStatus.textContent = 'Загрузка прошла успешно';
        uploadMessage.textContent = 'Ваш файл успешно загружен.';
        uploadStatus.style.display = 'block';
        uploadMessage.style.color = 'green';
    }
});

document.addEventListener('DOMContentLoaded', () => {
    // Функция для получения списка изображений
    async function fetchImages() {
        try {
            const response = await fetch('/api/images');
            if (!response.ok) {
                throw new Error('Не удалось загрузить изображения.');
            }
            const images = await response.json();
            renderImages(images);
        } catch (error) {
            console.error('Ошибка загрузки изображений:', error);
        }
    }

    // Функция для отрисовки списка изображений
    function renderImages(images) {
        const imageList = document.getElementById('image-list');
        imageList.innerHTML = ''; // Очищаем список

        images.forEach(image => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${image.name}</td>
                <td><a href="${image.url}" target="_blank">${image.url}</a></td>
                <td>
                    <button class="delete-btn" data-id="${image.id}"><i class="bi bi-trash-fill"></i></button>
                </td>
            `;
            imageList.appendChild(row);
        });
    }

    // Обработка клика на кнопку "Удалить"
    document.addEventListener('click', async (event) => {
        if (event.target.classList.contains('delete-btn')) {
            const deleteBtn = event.target;
            const imageId = deleteBtn.getAttribute('data-id');

            try {
                const response = await fetch(`/api/images/${imageId}`, {
                    method: 'DELETE'
                });

                if (!response.ok) {
                    throw new Error('Не удалось удалить изображение.');
                }

                // Обновляем список после удаления
                fetchImages();
            } catch (error) {
                console.error('Ошибка удаления изображения:', error);
            }
        }
    });

    // Загружаем список изображений при загрузке страницы
    fetchImages();
});