<!DOCTYPE html>
<html lang="en">

	<head>
	<link rel="stylesheet" type="text/css" href="cssdashboard.css" /> 
		<meta charset="utf-8" />
		<title> Akıllı ev sistemi: Dashboard </title>
	</head>
	
	<body>
		<!-- nav baslangic -->
		 <div class='nav'>
			<div class='menu'>
				<a class='left' href='#'><div class='menubutonu'>Anasayfa</div></a> 
				<a class='left' href='#'><div class='menubutonu'>Ev</div></a>  <!-- MEnu butonu için bu satırı kopyala -->
				<a class='left' href='#'><div class='menubutonu'>iletisim</div></a>
				<!-- dropdown buton baslangic -->
				<div class="dropdown">
				  <button class="dropbtn">Odalar</button>
				  <div class="dropdown-content">
					<a href='#'>Oda 1</a>
					<a href='#'>Oda 2</a>
					<a href='#'>Oda 3</a>
				  </div>
				</div>
				<!-- dropdown buton bitis -->
				<a class='right' href='#'><div class='loginbutonu'>Çıkış</div></a>
			</div>    
		</div>
		<!-- nav bitis -->
		
		<!-- content baslangic -->
		<div class='content'>
		
			<div class='left-bar'>
			
				<a class='left-bar-button' href='#'> <div class="lb-div">Sensör Değerleri</div> </a> 
				<a class='left-bar-button' href='#'> <div class="lb-div">Kamera</div> </a> 
				<a class='left-bar-button' href='#'> <div class="lb-div">Kontroller</div> </a> 
							
			</div>
			
			<div class='ana-content'> 
				<p> Güvenlik kamerasıyla çekilen son 5 kare.</p>
				<div id='gallery'>
				
					<div id='gallery-full'>
					
						<div><a name="pic1"></a><img alt="" src="http://deccoyi.bplaced.net/camera/buffer1.jpg" class='full-res'/></div>
						<div><a name="pic2"></a><img alt="" src="http://deccoyi.bplaced.net/camera/buffer2.jpg" class='full-res'/></div>
						<div><a name="pic3"></a><img alt="" src="http://deccoyi.bplaced.net/camera/buffer3.jpg" class='full-res'/></div>
						<div><a name="pic4"></a><img alt="" src="http://deccoyi.bplaced.net/camera/buffer4.jpg" class='full-res'/></div>
						<div><a name="pic5"></a><img alt="" src="http://deccoyi.bplaced.net/camera/buffer5.jpg" class='full-res'/></div>
					
					</div>
					<div id='gallery-nav'>
						<a href="#pic1"><img alt="" src="http://deccoyi.bplaced.net/camera/buffer1.jpg" class='mini-res'/></a>
						<a href="#pic2"><img alt="" src="http://deccoyi.bplaced.net/camera/buffer2.jpg" class='mini-res'/></a>
						<a href="#pic3"><img alt="" src="http://deccoyi.bplaced.net/camera/buffer3.jpg" class='mini-res'/></a>
						<a href="#pic4"><img alt="" src="http://deccoyi.bplaced.net/camera/buffer4.jpg" class='mini-res'/></a>
						<a href="#pic5"><img alt="" src="http://deccoyi.bplaced.net/camera/buffer5.jpg" class='mini-res'/></a>
					</div>
					
					
				</div>
			
			</div>
		
		</div>		
		<!-- content bitis -->
		
		<div class="footer">This footer will always be positioned at the bottom of the page, but <strong>not fixed</strong>.</div>
	
	</body>

</html>