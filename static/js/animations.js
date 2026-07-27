// ==========================================================================
// Marsh Family Practice — Cinematic Experience
// ==========================================================================

(function () {
    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var isTouch = window.matchMedia('(hover: none), (pointer: coarse)').matches;

    /* ---------------------------------------------------------------------
       0) Tag sections for photographic treatment
       --------------------------------------------------------------------- */
    document.querySelectorAll('section[style*="padding:60px 0 40px; background: linear-gradient(135deg, var(--bg-primary)"]')
        .forEach(function (el) { el.classList.add('photo-bg-page-hero'); });

    document.querySelectorAll('section[style*="background:var(--primary)"]')
        .forEach(function (el) { el.classList.add('photo-bg-cta'); });

    var heroEl = document.querySelector('.hero');
    var parallaxEls = Array.prototype.slice.call(
        document.querySelectorAll('.hero, .photo-bg-page-hero, .photo-bg-cta, .site-footer')
    );

    /* ---------------------------------------------------------------------
       1) Scroll-progress bar
       --------------------------------------------------------------------- */
    var progressBar = document.createElement('div');
    progressBar.id = 'scroll-progress';
    var progressFill = document.createElement('span');
    progressBar.appendChild(progressFill);
    document.body.appendChild(progressBar);

    /* ---------------------------------------------------------------------
       2) Scroll handler — progress bar + parallax offsets
       --------------------------------------------------------------------- */
    var ticking = false;
    function updateOnScroll() {
        var doc = document.documentElement;
        var scrollTop = window.scrollY || doc.scrollTop;
        var maxScroll = (doc.scrollHeight - doc.clientHeight) || 1;
        var progress = Math.min(Math.max(scrollTop / maxScroll, 0), 1);
        progressFill.style.transform = 'scaleX(' + progress + ')';

        if (!reduceMotion) {
            parallaxEls.forEach(function (el) {
                var rect = el.getBoundingClientRect();
                var center = rect.top + rect.height / 2 - window.innerHeight / 2;
                var offset = Math.max(Math.min(center * 0.06, 40), -40);
                el.style.setProperty('--py', offset.toFixed(1));
            });
        }
        ticking = false;
    }
    window.addEventListener('scroll', function () {
        if (!ticking) { requestAnimationFrame(updateOnScroll); ticking = true; }
    }, { passive: true });
    updateOnScroll();

    /* ---------------------------------------------------------------------
       3) Count-up for hero stats
       --------------------------------------------------------------------- */
    var statEls = document.querySelectorAll('.hero-stats .stat h3');
    function animateCount(el) {
        var raw = el.textContent.trim();
        var match = raw.match(/[\d,]+/);
        if (!match || reduceMotion) return;
        var target = parseInt(match[0].replace(/,/g, ''), 10);
        if (!target) return;
        var prefix = raw.slice(0, match.index);
        var suffix = raw.slice(match.index + match[0].length);
        var hasComma = match[0].indexOf(',') !== -1;
        var start = null, duration = 1200;
        function step(ts) {
            if (start === null) start = ts;
            var progress = Math.min((ts - start) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            var value = Math.round(target * eased);
            el.textContent = prefix + (hasComma ? value.toLocaleString('en-US') : value) + suffix;
            if (progress < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
    }
    if (statEls.length && 'IntersectionObserver' in window) {
        var statObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) { animateCount(entry.target); statObserver.unobserve(entry.target); }
            });
        }, { threshold: 0.5 });
        statEls.forEach(function (el) { statObserver.observe(el); });
    }

    /* ---------------------------------------------------------------------
       4) Pointer-tilt on elevated cards
       --------------------------------------------------------------------- */
    if (!reduceMotion && !isTouch) {
        document.querySelectorAll('.hero-card, .service-card, .testimonial-card, .panel, .booking-panel')
            .forEach(function (card) {
                var frame = null;
                card.addEventListener('mousemove', function (e) {
                    if (frame) cancelAnimationFrame(frame);
                    frame = requestAnimationFrame(function () {
                        var rect = card.getBoundingClientRect();
                        var x = (e.clientX - rect.left) / rect.width - 0.5;
                        var y = (e.clientY - rect.top) / rect.height - 0.5;
                        var maxTilt = 3.5;
                        card.style.transform =
                            'perspective(1200px) rotateX(' + (-y * maxTilt) + 'deg) rotateY(' + (x * maxTilt) + 'deg) translateY(-4px)';
                    });
                });
                card.addEventListener('mouseleave', function () {
                    if (frame) cancelAnimationFrame(frame);
                    card.style.transform = '';
                });
            });
    }

    /* ---------------------------------------------------------------------
       5) Decorative floating orbs
       --------------------------------------------------------------------- */
    if (!reduceMotion) {
        document.querySelectorAll('.photo-bg-cta').forEach(function (el) {
            el.classList.add('orb-host');
            [1, 2, 3].forEach(function (n) {
                var orb = document.createElement('div');
                orb.className = 'orb orb-' + n;
                el.appendChild(orb);
            });
        });
    }

    /* =====================================================================
       6) BACKGROUND VIDEOS - DISABLED (Handled in base.html)
       ===================================================================== */
    // Videos are now handled directly in base.html
    // No JavaScript video code needed here

    /* ---------------------------------------------------------------------
       7) Custom cursor
       --------------------------------------------------------------------- */
    if (!isTouch) {
        document.documentElement.classList.add('custom-cursor-active');
        var dot = document.createElement('div');
        dot.className = 'cursor-dot';
        var ring = document.createElement('div');
        ring.className = 'cursor-ring';
        document.body.appendChild(dot);
        document.body.appendChild(ring);

        var mouseX = -100, mouseY = -100;
        var ringX = -100, ringY = -100;

        window.addEventListener('mousemove', function (e) {
            mouseX = e.clientX;
            mouseY = e.clientY;
            dot.style.left = mouseX + 'px';
            dot.style.top = mouseY + 'px';
        });

        document.addEventListener('mouseover', function (e) {
            if (e.target.closest && e.target.closest('a, button, .btn, input, select, textarea, summary, label, .slot, .date-pill')) {
                ring.classList.add('is-hovering');
            }
        }, true);
        document.addEventListener('mouseout', function (e) {
            if (e.target.closest && e.target.closest('a, button, .btn, input, select, textarea, summary, label, .slot, .date-pill')) {
                ring.classList.remove('is-hovering');
            }
        }, true);

        (function tickRing() {
            var ease = reduceMotion ? 1 : 0.18;
            ringX += (mouseX - ringX) * ease;
            ringY += (mouseY - ringY) * ease;
            ring.style.left = ringX + 'px';
            ring.style.top = ringY + 'px';
            requestAnimationFrame(tickRing);
        })();
    }

    /* ---------------------------------------------------------------------
       8) WebGL particle field (Three.js)
       --------------------------------------------------------------------- */
    function initHeroParticles(hero) {
        if (!window.THREE || reduceMotion) return null;

        var canvas = document.createElement('canvas');
        canvas.className = 'webgl-layer';
        canvas.style.position = 'absolute';
        canvas.style.inset = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.pointerEvents = 'none';
        canvas.style.zIndex = '-1';
        hero.appendChild(canvas);

        var renderer;
        try {
            renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
        } catch (err) {
            canvas.remove();
            return null;
        }
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

        var scene = new THREE.Scene();
        var camera = new THREE.PerspectiveCamera(55, 1, 0.1, 100);
        camera.position.z = 18;

        var count = window.innerWidth < 768 ? 450 : 1100;
        var positions = new Float32Array(count * 3);
        for (var i = 0; i < count; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 42;
            positions[i * 3 + 1] = (Math.random() - 0.5) * 26;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 22;
        }
        var geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

        var spriteCanvas = document.createElement('canvas');
        spriteCanvas.width = spriteCanvas.height = 64;
        var sctx = spriteCanvas.getContext('2d');
        var grad = sctx.createRadialGradient(32, 32, 0, 32, 32, 32);
        grad.addColorStop(0, 'rgba(255,255,255,0.95)');
        grad.addColorStop(0.4, 'rgba(221,181,112,0.55)');
        grad.addColorStop(1, 'rgba(221,181,112,0)');
        sctx.fillStyle = grad;
        sctx.fillRect(0, 0, 64, 64);
        var spriteTexture = new THREE.CanvasTexture(spriteCanvas);

        var material = new THREE.PointsMaterial({
            size: 0.26,
            map: spriteTexture,
            transparent: true,
            depthWrite: false,
            blending: THREE.AdditiveBlending,
            opacity: 0.8
        });
        var points = new THREE.Points(geometry, material);
        scene.add(points);

        function resize() {
            var w = hero.clientWidth, h = hero.clientHeight;
            if (!w || !h) return;
            renderer.setSize(w, h);
            camera.aspect = w / h;
            camera.updateProjectionMatrix();
        }
        resize();
        window.addEventListener('resize', resize);

        var targetX = 0, targetY = 0;
        hero.addEventListener('mousemove', function (e) {
            var r = hero.getBoundingClientRect();
            targetX = ((e.clientX - r.left) / r.width - 0.5) * 2;
            targetY = ((e.clientY - r.top) / r.height - 0.5) * 2;
        });

        var running = true;
        function animate() {
            if (!running) return;
            points.rotation.y += 0.0009;
            points.rotation.x += 0.00025;
            camera.position.x += (targetX * 1.6 - camera.position.x) * 0.03;
            camera.position.y += (-targetY * 1.0 - camera.position.y) * 0.03;
            camera.lookAt(scene.position);
            renderer.render(scene, camera);
            requestAnimationFrame(animate);
        }
        animate();

        if ('IntersectionObserver' in window) {
            new IntersectionObserver(function (entries) {
                running = entries[0].isIntersecting;
                if (running) animate();
            }, { threshold: 0 }).observe(hero);
        }

        return canvas;
    }

    if (heroEl) {
        var heroCanvas = initHeroParticles(heroEl);
    }

    /* ---------------------------------------------------------------------
       9) GSAP + ScrollTrigger (if available)
       --------------------------------------------------------------------- */
    var hasGSAP = !!(window.gsap && window.ScrollTrigger);

    if (!hasGSAP || reduceMotion) {
        var revealTargets = document.querySelectorAll('.reveal');
        var siblingIndex = new WeakMap();
        revealTargets.forEach(function (el) {
            var parent = el.parentElement;
            var n = siblingIndex.get(parent) || 0;
            el.style.setProperty('--reveal-delay', Math.min(n * 0.08, 0.4) + 's');
            siblingIndex.set(parent, n + 1);
        });
        if (reduceMotion || !('IntersectionObserver' in window)) {
            revealTargets.forEach(function (el) { el.classList.add('in-view'); });
        } else {
            var io = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) { entry.target.classList.add('in-view'); io.unobserve(entry.target); }
                });
            }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
            revealTargets.forEach(function (el) { io.observe(el); });
        }
        return;
    }

    gsap.registerPlugin(ScrollTrigger);

    if (heroEl) {
        var introParts = [
            heroEl.querySelector('.hero-badge'),
            heroEl.querySelector('.hero-content h1'),
            heroEl.querySelector('.hero-content > p'),
            heroEl.querySelector('.hero-actions'),
            heroEl.querySelector('.hero-stats')
        ].filter(Boolean);

        gsap.set(introParts, { opacity: 0, y: 26 });
        gsap.to(introParts, {
            opacity: 1, y: 0, duration: 0.8, ease: 'power3.out', stagger: 0.12, delay: 0.2
        });
    }

    if (heroEl) {
        var heroContent = heroEl.querySelector('.hero-content');
        var heroCard = heroEl.querySelector('.hero-card');

        ScrollTrigger.create({
            trigger: heroEl,
            start: 'top top',
            end: '+=55%',
            pin: true,
            pinSpacing: true,
            scrub: 0.6,
            onUpdate: function (self) {
                var p = self.progress;
                if (heroContent) {
                    heroContent.style.opacity = 1 - p;
                    heroContent.style.transform = 'translateY(' + (p * -70) + 'px) scale(' + (1 - p * 0.06) + ')';
                }
                if (heroCard) {
                    heroCard.style.opacity = 1 - p;
                    heroCard.style.transform = 'translateY(' + (p * 40) + 'px) scale(' + (1 - p * 0.05) + ')';
                }
            }
        });
    }

    gsap.utils.toArray('.reveal').forEach(function (el) {
        gsap.fromTo(el,
            { opacity: 0, y: 46, scale: 0.96, filter: 'blur(6px)' },
            {
                opacity: 1, y: 0, scale: 1, filter: 'blur(0px)',
                ease: 'none',
                scrollTrigger: { trigger: el, start: 'top 92%', end: 'top 55%', scrub: 0.4 }
            }
        );
    });

    var testimonialGrid = document.querySelector('.testimonials-grid');
    if (testimonialGrid && testimonialGrid.children.length > 1) {
        var section = testimonialGrid.closest('.section') || testimonialGrid.parentElement;
        testimonialGrid.classList.add('horizontal-scroll');
        section.style.overflow = 'hidden';

        ScrollTrigger.create({
            trigger: section,
            start: 'top top',
            end: function () { return '+=' + (testimonialGrid.scrollWidth - window.innerWidth + 300); },
            pin: true,
            scrub: 0.8,
            invalidateOnRefresh: true,
            onUpdate: function (self) {
                var maxX = testimonialGrid.scrollWidth - window.innerWidth + 80;
                testimonialGrid.style.transform = 'translateX(' + (-self.progress * Math.max(maxX, 0)) + 'px)';
            }
        });
    }

    window.addEventListener('load', function () { 
        if (window.ScrollTrigger) {
            ScrollTrigger.refresh(); 
        }
    });
})();