if (screen.width >= 991) {
    (function() {
        'use strict';

        var camera, scene, renderer,
            container, particle,
            winHalfX, winHalfY,
            height, width, fieldOfView,
            aspectRatio, nearPlane, farPlane,
            body, cameraZ, material,
            i = 0,
            count = 0,
            Tau = Math.PI * 2,
            mouseX = 0,
            mouseY = 0,
            amtX = 50,
            amtY = 50,
            sep = 100,
            spriteOpts = {},
            particles = [],
            cssString = 'margin: 0;';

        function onDocumentReady() {
            body = document.body;
            body.style.cssText = cssString;

            container = document.createElement('polyWorld');
            body.appendChild(container);

            height = window.innerHeight;
            winHalfY = height / 2;
            width = window.innerWidth;
            winHalfX = width / 2;
            fieldOfView = 75;
            aspectRatio = width / height;
            nearPlane = 1;
            farPlane = 10000;
            cameraZ = 750;

            rendererer(onRendererRenderered);
        }

        // renders the renderer
        function rendererer(complete) {
            camera = new THREE.PerspectiveCamera(fieldOfView, aspectRatio, nearPlane, farPlane);
            camera.position.z = cameraZ;

            scene = new THREE.Scene();

            //material settings
            spriteOpts = {
                color: 0xffffff,
                program: function(ctx) {
                    ctx.beginPath();
                    ctx.arc(0, 0, 0.5, 0, Tau, true);
                    ctx.fill();
                }
            };

            material = new THREE.SpriteCanvasMaterial(spriteOpts);

            // particle time!
            for (var ix = 0, lx = amtX; ix < lx; ix++) {

                for (var iy = 0, ly = amtY; iy < ly; iy++) {
                    particle = particles[i++] = new THREE.Sprite(material);
                    particle.position.x = ix * sep - ((amtX * sep) / 2);
                    particle.position.z = iy * sep - ((amtY * sep) / 2);
                    scene.add(particle);
                }
            }

            //render the scene
            renderer = new THREE.CanvasRenderer( { alpha: true });
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.setSize(width, height);

            // append the rendered scene to the container
            container.appendChild(renderer.domElement);

            // aaaaaaaaand Scene
            if (complete) {
                complete();
            }
        }

        function onRendererRenderered() {
            // bind events
            document.addEventListener('mousemove', onDocumentMouseMove);
            document.addEventListener('touchstart', onDocumentTouchStart);
            document.addEventListener('touchmove', onDocumentTouchMove);
            window.addEventListener('resize', onWindowResize);

        }

        function onDocumentMouseMove(e) {
            mouseX = e.clientX - winHalfX;
            mouseY = e.clientY - winHalfY;
        }

        function onDocumentTouchStart(e) {
            if (e.touches.length === 1) {
                e.preventDefault();
                mouseX = e.touches[0].pageX - winHalfX;
                mouseY = e.touches[0].pageY - winHalfY;
            }
        }

        function onDocumentTouchMove(e) {
            if (e.touches.length === 1) {
                e.preventDefault();
                mouseX = e.touches[0].pageX - winHalfX;
                mouseY = e.touches[0].pageY - winHalfY;
            }
        }

        function onWindowResize() {
            // update variables to new values
            height = window.innerHeight;
            winHalfY = height / 2;
            width = window.innerWidth;
            winHalfX = width / 2;

            camera.aspect = width / height;
            camera.updateProjectionMatrix();
            renderer.setSize(width, height);
        }

        function animate() {
            requestAnimationFrame(animate);

            update();
        }

        function update() {
            camera.position.x += (mouseX - camera.position.x) * 0.05;
            camera.position.y += (mouseY - camera.position.y) * 0.05;
            camera.lookAt(scene.position);

            i = 0;
            for (var ix = 0, lx = amtX; ix < lx; ix++) {

                for (var iy = 0, ly = amtY; iy < ly; iy++) {
                    particle = particles[i++];
                    particle.position.y = (Math.sin((ix + count) * 0.3) * 50) + (Math.sin((iy + count) * 0.5) * 50);
                    particle.scale.x = particle.scale.y = (Math.sin((ix + count) * 0.3) + 1) * 4 + (Math.sin((iy + count) * 0.5) + 1) * 4;
                    scene.add(particle);
                }
            }

            renderer.render(scene, camera);
            count += 0.1;
        }

        document.addEventListener('DOMContentLoaded', onDocumentReady);
        document.addEventListener('DOMContentLoaded', animate);

    })();
}