// -------------------------------------------------------------
// 1. Language Toggle & Translation Engine
// -------------------------------------------------------------
const langBtn = document.getElementById('lang-toggle');
const languages = ['uz', 'ru', 'en'];
let currentLang = 'uz'; // Default to UZ

const translatableElements = document.querySelectorAll('[data-ru]');

function updateLanguage(lang) {
    currentLang = lang;
    if (langBtn) {
        langBtn.textContent = lang.toUpperCase();
    }
    
    translatableElements.forEach(el => {
        const text = el.getAttribute('data-' + lang);
        if (text) {
            // Check if element is a button or simple text container
            if (el.tagName === 'INPUT' && (el.type === 'button' || el.type === 'submit')) {
                el.value = text;
            } else {
                el.textContent = text;
            }
        }
    });

    // Refresh interactive terminal text language if applicable
    const activeCmd = document.getElementById('terminal-interactive-cmd');
    if (activeCmd) {
        runTermCmd(activeCmd.textContent, true);
    }
}

if (langBtn) {
    langBtn.addEventListener('click', () => {
        const currentIndex = languages.indexOf(currentLang);
        const nextIndex = (currentIndex + 1) % languages.length;
        updateLanguage(languages[nextIndex]);
        
        // Add click feedback animation
        langBtn.style.transform = 'scale(0.9) rotate(5deg)';
        setTimeout(() => {
            langBtn.style.transform = 'scale(1) rotate(0deg)';
        }, 150);
    });
}

// -------------------------------------------------------------
// 2. Matrix Rain Simulation
// -------------------------------------------------------------
const canvas = document.getElementById('matrix');
if (canvas) {
    const ctx = canvas.getContext('2d');

    // Set full screen width/height
    const resizeCanvas = () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Matrix characters (binary + hex + katakana for standard matrix rain)
    const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789日ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾏｹﾒｴｶｷﾑﾕﾗｾﾈｽﾀﾇﾍｦｲｸｺｿﾁﾄﾉﾌﾔﾖﾙﾚﾛﾝ';
    const charArray = chars.split('');

    const fontSize = 14;
    let columns = canvas.width / fontSize;

    // Drops coordinates y values
    let drops = [];
    for (let i = 0; i < columns; i++) {
        drops[i] = Math.random() * -100; // staggered start heights
    }

    const drawMatrix = () => {
        // Semi-transparent background to create trailing effect
        ctx.fillStyle = 'rgba(2, 2, 4, 0.08)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#00ff66'; // Glowing Matrix Green
        ctx.font = fontSize + 'px monospace';

        for (let i = 0; i < drops.length; i++) {
            // Pick a random character
            const text = charArray[Math.floor(Math.random() * charArray.length)];
            
            // Render the character
            const x = i * fontSize;
            const y = drops[i] * fontSize;

            // Randomize brightness
            if (Math.random() > 0.98) {
                ctx.fillStyle = '#ffffff'; // White tip
            } else {
                ctx.fillStyle = 'rgba(0, 255, 102, ' + (Math.random() * 0.5 + 0.5) + ')';
            }

            ctx.fillText(text, x, y);

            // Reset drop to top once it goes past screen height
            if (y > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }

            drops[i]++;
        }
    };

    // Render at roughly 30 FPS for performance
    setInterval(drawMatrix, 35);
}

// -------------------------------------------------------------
// 3. Interactive Terminal Command Simulator
// -------------------------------------------------------------
const terminalResponses = {
    help: {
        uz: `TIZIM BUYRUQLARI // SYSTEM COMMANDS:\n` +
            `- modules: Akademiyaning barcha o'quv modullarini tekshirish\n` +
            `- secure: Total Security xavfsizlik shifrlarini tahlil qilish\n` +
            `- status: Platformaning onlayn ish holatini ko'rish\n` +
            `- clear: Terminal ekranini tozalash`,
        ru: `СИСТЕМНЫЕ КОМАНДЫ // SYSTEM COMMANDS:\n` +
            `- modules: Показать все учебные модули Академии\n` +
            `- secure: Проанализировать протоколы Total Security\n` +
            `- status: Проверить онлайн статус платформы\n` +
            `- clear: Очистить экран терминала`,
        en: `SYSTEM COMMANDS // SYSTEM COMMANDS:\n` +
            `- modules: Show all educational modules of Academy\n` +
            `- secure: Analyze Total Security shield protocols\n` +
            `- status: Check platform server online health\n` +
            `- clear: Clear terminal screen`
    },
    modules: {
        uz: `YUKSAK ACADEMY KO'CHIRILGAN MODULLAR:\n` +
            `[MOD_01] Python & Telegram Botlar yaratish (IT)\n` +
            `[MOD_02] Dizayn & Sun'iy Intellekt (AI)\n` +
            `[MOD_03] 3D Modellashtirish (Blender, 3ds Max)\n` +
            `[MOD_04] Rus va Ingliz tillari akademiyasi\n` +
            `>> Barchasi faol. Telegram bot orqali ishlaydi.`,
        ru: `ЗАГРУЖЕННЫЕ МОДУЛИ YUKSAK ACADEMY:\n` +
            `[MOD_01] Python & Создание Telegram Ботов (IT)\n` +
            `[MOD_02] Дизайн & Искусственный Интеллект (AI)\n` +
            `[MOD_03] 3D Моделирование (Blender, 3ds Max)\n` +
            `[MOD_04] Академия Русского и Английского языков\n` +
            `>> Все модули АКТИВНЫ. Обучение проходит в Telegram боте.`,
        en: `LOADED MODULES YUKSAK ACADEMY:\n` +
            `[MOD_01] Python & Telegram Bot Creation (IT)\n` +
            `[MOD_02] Design & Artificial Intelligence (AI)\n` +
            `[MOD_03] 3D Modeling (Blender, 3ds Max)\n` +
            `[MOD_04] Russian & English Language Academy\n` +
            `>> All modules online. Learning happens inside Telegram bot.`
    },
    secure: {
        uz: `TOTAL SECURITY SYSTEM SCAN REPORT:\n` +
            `[PROTECT-1] Nusxalashni taqiqlash: FAOL (Video yuklab bo'lmaydi)\n` +
            `[PROTECT-2] Anti-Xaker FireWall: ISHLAMOQDA (Buzg'unchilar auto-bloklanadi)\n` +
            `[PROTECT-3] Shaxsiy ma'lumotlar shifrlandi (AES-256 standard)\n` +
            `>> XAVFSIZLIK DARAJASI: 100% MAKSIMAL`,
        ru: `TOTAL SECURITY SYSTEM SCAN REPORT:\n` +
            `[PROTECT-1] Запрет копирования: АКТИВЕН (Загрузка видео заблокирована)\n` +
            `[PROTECT-2] Анти-Хакер FireWall: ЗАПУЩЕН (Моментальный авто-бан нарушителей)\n` +
            `[PROTECT-3] База данных зашифрована по стандарту AES-256\n` +
            `>> СТАТУС БЕЗОПАСНОСТИ: 100% МАКСИМАЛЬНЫЙ`,
        en: `TOTAL SECURITY SYSTEM SCAN REPORT:\n` +
            `[PROTECT-1] Copy protection: ACTIVE (Video downloads prohibited)\n` +
            `[PROTECT-2] Anti-Hacker FireWall: RUNNING (Instant intruder auto-block)\n` +
            `[PROTECT-3] Databases encrypted using AES-256 standard\n` +
            `>> SECURITY SHIELD: 100% MAXIMUM STRENGTH`
    },
    status: {
        uz: `TIZIM PARAMETRLARI // SYSTEM METRICS:\n` +
            `- Server statusi: ONLAYN (100% Faol)\n` +
            `- Sun'iy intellekt (AI): ALOQA O'RNATILDI (Uptime: 99.9%)\n` +
            `- Telegram Bot API: INTEGRATSIYA QILINGAN\n` +
            `- Asoschi: KAMOLOV.A // Platforma tayyor.`,
        ru: `ПАРАМЕТРЫ СИСТЕМЫ // SYSTEM METRICS:\n` +
            `- Статус сервера: ОНЛАЙН (100% Активен)\n` +
            `- Искусственный Интеллект: ПОДКЛЮЧЕН (Uptime: 99.9%)\n` +
            `- Telegram Bot API: УСПЕШНАЯ ИНТЕГРАЦИЯ\n` +
            `- Основатель: KAMOLOV.A // Платформа готова к работе.`,
        en: `SYSTEM METRICS // SYSTEM METRICS:\n` +
            `- Server status: ONLINE (100% Active)\n` +
            `- Artificial Intelligence: CONNECTED (Uptime: 99.9%)\n` +
            `- Telegram Bot API: INTEGRATED SUCCESSFULLY\n` +
            `- Founder: KAMOLOV.A // Platform ready for deployment.`
    }
};

window.runTermCmd = function(cmd, quiet = false) {
    const cmdSpan = document.getElementById('terminal-interactive-cmd');
    const outputDiv = document.getElementById('terminal-interactive-output');
    
    if (!cmdSpan || !outputDiv) return;

    if (cmd === 'clear') {
        cmdSpan.textContent = 'clear';
        outputDiv.innerHTML = '';
        return;
    }

    cmdSpan.textContent = cmd;

    const responseObj = terminalResponses[cmd];
    if (responseObj) {
        const responseText = responseObj[currentLang] || responseObj['uz'];
        // Format newlines into HTML breaks
        outputDiv.innerHTML = responseText.replace(/\n/g, '<br>');
        
        // Add a sleek glowing flash animation to terminal output
        if (!quiet) {
            outputDiv.style.opacity = '0';
            setTimeout(() => {
                outputDiv.style.opacity = '1';
                outputDiv.style.textShadow = '0 0 8px rgba(0, 255, 102, 0.6)';
                setTimeout(() => outputDiv.style.textShadow = 'none', 300);
            }, 50);
        }
    } else {
        outputDiv.textContent = `yuksak: command not found: ${cmd}`;
    }
};

// -------------------------------------------------------------
// 4. Scroll Reveal IntersectionObserver
// -------------------------------------------------------------
if ('IntersectionObserver' in window) {
    const scrollOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -40px 0px'
    };

    const scrollObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('aos-animate');
                scrollObserver.unobserve(entry.target);
            }
        });
    }, scrollOptions);

    document.querySelectorAll('[data-aos]').forEach(el => {
        scrollObserver.observe(el);
    });
} else {
    // Fallback for older browsers
    document.querySelectorAll('[data-aos]').forEach(el => {
        el.style.opacity = '1';
        el.style.transform = 'none';
    });
}

// -------------------------------------------------------------
// 5. Navbar Sticky Dynamics
// -------------------------------------------------------------
const navbar = document.querySelector('.navbar');
if (navbar) {
    window.addEventListener('scroll', () => {
        if (window.scrollY > 80) {
            navbar.style.top = '0.5rem';
            navbar.style.background = 'rgba(2, 2, 4, 0.95)';
            navbar.style.borderColor = 'rgba(0, 255, 102, 0.4)';
            navbar.style.boxShadow = '0 12px 40px rgba(0, 255, 102, 0.12)';
        } else {
            navbar.style.top = '1.5rem';
            navbar.style.background = 'rgba(3, 3, 5, 0.85)';
            navbar.style.borderColor = 'rgba(0, 255, 102, 0.2)';
            navbar.style.boxShadow = '0 8px 32px rgba(0,0,0,0.8)';
        }
    });
}

console.log('YUKSAK ACADEMY Cyber-Deck Loaded.');
