pyinstaller main.py \
	--clean \
	-D \
	--name "Course tracker" \
	--add-data 'images:images' \
	-i 'images/main_icon.ico' 
