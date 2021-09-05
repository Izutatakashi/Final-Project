document.addEventListener('DOMContentLoaded', function() {//add event listener - DOMC2

/////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////

	document.addEventListener("mousedown", function (event) { //add event listener - keydown
		document.oncopy = function()
							{
								return false;

							}
		document.oncut = function(){return false;}
		document.onpaste = function(){return false;}

		if(event.button==2)	{
			; //alert("Right click disabled");
		}
     return false;

    });

/////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////

	let ControlPressed= false;

	document.addEventListener("keydown", function onEvent(event) { //add event listener - keydown

		if (event.key==="Control"){
			ControlPressed=true;
		}

		if (ControlPressed && (event.code === "KeyC" || event.code === "KeyV"))
			return false;
    });//add event listener - keydown

////////////////////////////

	document.addEventListener("keyup", function onEvent(event) { //add event listener - keyup

		if (event.key==="Control"){
			ControlPressed=false;
		}

    });//add event listener - keyup

/////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////



}); //add event listener - DOMC2