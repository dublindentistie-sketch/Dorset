// 标签页切换功能
document.addEventListener('DOMContentLoaded', function() {
    // 移动端导航菜单
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const mainNavLinks = document.getElementById('navLinks');
    const navLinks = document.querySelectorAll('.services-nav a');
    const sections = document.querySelectorAll('.service-category');
    const categoryToggle = document.getElementById('categoryToggle');
    const servicesNav = document.querySelector('.services-nav');

    // 汉堡菜单切换
    if (mobileMenuToggle && mainNavLinks) {
        mobileMenuToggle.addEventListener('click', function() {
            this.classList.toggle('active');
            mainNavLinks.classList.toggle('active');
        });

        // 点击导航链接后关闭菜单
        const mainNavLinksItems = mainNavLinks.querySelectorAll('a');
        mainNavLinksItems.forEach(link => {
            link.addEventListener('click', function() {
                mobileMenuToggle.classList.remove('active');
                mainNavLinks.classList.remove('active');
            });
        });

        // 点击页面其他地方关闭菜单
        document.addEventListener('click', function(event) {
            if (!event.target.closest('nav')) {
                mobileMenuToggle.classList.remove('active');
                mainNavLinks.classList.remove('active');
            }
        });
    }

    // 默认显示第一个分类
    if (sections.length > 0) {
        sections.forEach((section, index) => {
            section.style.display = index === 0 ? 'block' : 'none';
        });
        if (navLinks.length > 0) {
            navLinks[0].classList.add('active');
        }
    }

    // 移动端分类切换按钮
    if (categoryToggle && servicesNav) {
        categoryToggle.addEventListener('click', function() {
            servicesNav.classList.toggle('show');
            this.classList.toggle('active');

            if (servicesNav.classList.contains('show')) {
                this.textContent = 'Hide Categories';
            } else {
                this.textContent = 'Show Categories';
            }
        });
    }

    // 点击导航切换分类
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            // 移除所有active类
            navLinks.forEach(l => l.classList.remove('active'));

            // 添加active到当前链接
            this.classList.add('active');

            // 获取目标分类ID
            const targetId = this.getAttribute('href').substring(1);

            // 隐藏所有分类，显示目标分类
            sections.forEach(section => {
                if (section.id === targetId) {
                    section.style.display = 'block';
                } else {
                    section.style.display = 'none';
                }
            });

            // 在移动端点击分类后自动隐藏导航
            if (window.innerWidth <= 768 && categoryToggle && servicesNav) {
                servicesNav.classList.remove('show');
                categoryToggle.classList.remove('active');
                categoryToggle.textContent = 'Show Categories';
            }
        });
    });

    // 多步骤预约表单处理
    const appointmentForm = document.getElementById('appointmentForm');
    const formMessage = document.getElementById('formMessage');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const submitBtn = document.getElementById('submitBtn');
    const formSteps = document.querySelectorAll('.form-step');
    const progressSteps = document.querySelectorAll('.step');

    let currentStep = 1;
    const totalSteps = 4;

    if (appointmentForm) {
        // 设置日期输入的最小值为今天
        const dateInput = document.getElementById('appointmentDate');
        if (dateInput) {
            const today = new Date().toISOString().split('T')[0];
            dateInput.setAttribute('min', today);
        }

        // 处理自定义服务输入显示/隐藏
        const serviceTypeSelect = document.getElementById('serviceType');
        const customServiceGroup = document.getElementById('customServiceGroup');
        const customServiceInput = document.getElementById('customService');

        serviceTypeSelect.addEventListener('change', function() {
            if (this.value === 'custom') {
                customServiceGroup.style.display = 'block';
                customServiceInput.setAttribute('required', 'required');
            } else {
                customServiceGroup.style.display = 'none';
                customServiceInput.removeAttribute('required');
                customServiceInput.value = '';
            }
        });

        // 上一步按钮
        prevBtn.addEventListener('click', function() {
            if (currentStep > 1) {
                currentStep--;
                updateFormStep();
            }
        });

        // 下一步按钮
        nextBtn.addEventListener('click', function() {
            if (validateCurrentStep()) {
                if (currentStep < totalSteps) {
                    currentStep++;
                    updateFormStep();

                    // 如果到达确认页面，显示确认信息
                    if (currentStep === 4) {
                        updateConfirmation();
                    }
                }
            }
        });

        // 表单提交
        appointmentForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // 获取表单数据
            const serviceType = document.getElementById('serviceType').value;
            const customService = document.getElementById('customService').value;

            const formData = {
                name: document.getElementById('patientName').value,
                email: document.getElementById('patientEmail').value,
                phone: document.getElementById('patientPhone').value,
                date: document.getElementById('appointmentDate').value,
                time: document.getElementById('appointmentTime').value,
                service: serviceType,
                custom_service: serviceType === 'custom' ? customService : '',
                message: document.getElementById('patientMessage').value
            };

            // 验证日期是否为工作日
            const selectedDate = new Date(formData.date);
            const dayOfWeek = selectedDate.getDay();

            if (dayOfWeek === 0) { // Sunday
                showMessage('Sorry, we are closed on Sundays. Please select another date.', 'error');
                return;
            }

            // 验证时间是否在营业时间内
            const timeValue = parseInt(formData.time.split(':')[0]);
            if (dayOfWeek === 6) { // Saturday
                if (timeValue < 10 || timeValue >= 16) {
                    showMessage('Saturday hours are 10:00 AM - 4:00 PM. Please select a valid time.', 'error');
                    return;
                }
            } else { // Weekdays
                if (timeValue < 9 || timeValue >= 18) {
                    showMessage('Weekday hours are 9:00 AM - 6:00 PM. Please select a valid time.', 'error');
                    return;
                }
            }

            // 发送预约数据到Django后端
            fetch('/api/appointments/create/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showMessage(data.message, 'success');
                    // 重置表单
                    setTimeout(() => {
                        appointmentForm.reset();
                        currentStep = 1;
                        updateFormStep();
                        formMessage.style.display = 'none';
                    }, 3000);
                } else {
                    showMessage(data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('An error occurred while submitting your appointment. Please try again.', 'error');
            });
        });

        // 更新表单步骤显示
        function updateFormStep() {
            // 更新表单步骤内容
            formSteps.forEach((step, index) => {
                if (index + 1 === currentStep) {
                    step.classList.add('active');
                } else {
                    step.classList.remove('active');
                }
            });

            // 更新进度指示器
            progressSteps.forEach((step, index) => {
                if (index + 1 < currentStep) {
                    step.classList.add('completed');
                    step.classList.remove('active');
                } else if (index + 1 === currentStep) {
                    step.classList.add('active');
                    step.classList.remove('completed');
                } else {
                    step.classList.remove('active', 'completed');
                }
            });

            // 更新按钮显示
            if (currentStep === 1) {
                prevBtn.style.display = 'none';
            } else {
                prevBtn.style.display = 'block';
            }

            if (currentStep === totalSteps) {
                nextBtn.style.display = 'none';
                submitBtn.style.display = 'block';
            } else {
                nextBtn.style.display = 'block';
                submitBtn.style.display = 'none';
            }

            // 滚动到表单顶部
            appointmentForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        // 验证当前步骤
        function validateCurrentStep() {
            const currentFormStep = document.querySelector(`.form-step[data-step="${currentStep}"]`);
            const inputs = currentFormStep.querySelectorAll('input[required], select[required]');

            for (let input of inputs) {
                if (!input.value) {
                    input.focus();
                    showMessage('Please fill in all required fields.', 'error');
                    setTimeout(() => {
                        formMessage.style.display = 'none';
                    }, 3000);
                    return false;
                }

                // 验证邮箱格式
                if (input.type === 'email' && !isValidEmail(input.value)) {
                    input.focus();
                    showMessage('Please enter a valid email address.', 'error');
                    setTimeout(() => {
                        formMessage.style.display = 'none';
                    }, 3000);
                    return false;
                }
            }

            return true;
        }

        // 邮箱验证
        function isValidEmail(email) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(email);
        }

        // 更新确认页面信息
        function updateConfirmation() {
            const serviceSelect = document.getElementById('serviceType');
            const selectedServiceText = serviceSelect.options[serviceSelect.selectedIndex].text;
            const customService = document.getElementById('customService').value;
            const message = document.getElementById('patientMessage').value;

            document.getElementById('confirmName').textContent = document.getElementById('patientName').value;
            document.getElementById('confirmEmail').textContent = document.getElementById('patientEmail').value;
            document.getElementById('confirmPhone').textContent = document.getElementById('patientPhone').value;

            // 如果是自定义服务，显示用户输入的服务名称
            if (serviceSelect.value === 'custom' && customService) {
                document.getElementById('confirmService').textContent = customService;
            } else {
                document.getElementById('confirmService').textContent = selectedServiceText;
            }

            document.getElementById('confirmDate').textContent = formatDate(document.getElementById('appointmentDate').value);
            document.getElementById('confirmTime').textContent = formatTime(document.getElementById('appointmentTime').value);

            // 显示或隐藏备注
            if (message) {
                document.getElementById('confirmMessage').textContent = message;
                document.getElementById('confirmMessageContainer').style.display = 'flex';
            } else {
                document.getElementById('confirmMessageContainer').style.display = 'none';
            }
        }

        // 格式化日期
        function formatDate(dateString) {
            const date = new Date(dateString);
            const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
            return date.toLocaleDateString('en-US', options);
        }

        // 格式化时间
        function formatTime(timeString) {
            const [hours, minutes] = timeString.split(':');
            const hour = parseInt(hours);
            const ampm = hour >= 12 ? 'PM' : 'AM';
            const displayHour = hour > 12 ? hour - 12 : hour;
            return `${displayHour}:${minutes} ${ampm}`;
        }
    }

    function showMessage(message, type) {
        formMessage.textContent = message;
        formMessage.className = 'form-message ' + type;
        formMessage.style.display = 'block';
    }

    // 获取CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
