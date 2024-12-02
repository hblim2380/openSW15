const cartSidebar = document.getElementById('cartSidebar');
const cartOverlay = document.querySelector('.cart-overlay');

document.addEventListener("DOMContentLoaded", function () {
        const tabs = document.querySelectorAll(".nav-link");
        const menuItems = document.querySelectorAll(".menu-item");

        tabs.forEach(tab => {
            tab.addEventListener("click", function () {
                const category = this.textContent.trim();
                tabs.forEach(t => t.classList.remove("active"));
                this.classList.add("active");

                menuItems.forEach(item => {
                    const itemCategory = item.dataset.category;
                    item.style.display = category === "전체" || itemCategory === category ? "block" : "none";
                });
            });
        });
    });
    
    const Cart = {
        items: [],
        addItem(item) {
            this.items.push(item);
            this.updateCartView();
        },
        removeItem(index) {
            this.items.splice(index, 1);
            this.updateCartView();
        },
        calculateTotal() {
            return this.items.reduce((total, item) => total + item.totalPrice, 0);
        },
        updateCartView() {
            const cartContainer = document.getElementById('cartItemsContainer');
            const totalPriceElement = document.getElementById('cartTotalPrice');

            cartContainer.innerHTML = ''; // 장바구니 항목 초기화

            this.items.forEach((item, index) => {
                const cartItemElement = document.createElement('div');
                cartItemElement.classList.add('cart-item');
                cartItemElement.innerHTML = `
                <div>
                    <strong>${item.name}</strong>
                    <br>수량: ${item.quantity}
                    ${item.toppings.length > 0 ? `<br>토핑: ${item.toppings.join(', ')}` : ''}
                </div>
                <div>
                    <span>${item.totalPrice.toLocaleString()}원</span>
                    <button class="btn btn-sm btn-danger ms-2 remove-item" data-index="${index}">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            `;
                cartContainer.appendChild(cartItemElement);
            });

            totalPriceElement.textContent = `총 금액: ${this.calculateTotal().toLocaleString()}원`; // 총 금액 표시

            cartContainer.querySelectorAll('.remove-item').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const index = e.currentTarget.dataset.index;
                    this.removeItem(index);
                });
            });
        }
    };

    const menuGrid = document.getElementById('menuGrid');
    if (menuGrid) {
        menuGrid.addEventListener('click', (e) => {
            const menuItem = e.target.closest('.menu-item');
            if (menuItem) {
                const menuName = menuItem.dataset.name;
                const menuPrice = parseInt(menuItem.dataset.price);
                const menuModal = new bootstrap.Modal(document.getElementById('menuOptionsModal'));

                document.getElementById('menuOptionModalTitle').textContent = `${menuName} 옵션 선택`;

                document.getElementById('addToCartBtn').onclick = () => {
                    const selectedToppings = Array.from(
                        document.querySelectorAll('input[name="toppings"]:checked')
                    ).map(el => el.nextElementSibling.textContent);

                    const quantity = document.getElementById('quantity').value;
                    const toppingPrice = Array.from(
                        document.querySelectorAll('input[name="toppings"]:checked')
                    ).reduce((sum, el) => sum + parseInt(el.value), 0);

                    const napkinPrice = document.getElementById('napkin').checked ? 100 : 0;

                    const totalPrice = (menuPrice + toppingPrice + napkinPrice) * quantity;

                    Cart.addItem({
                        name: menuName,
                        quantity: quantity,
                        toppings: selectedToppings,
                        totalPrice: totalPrice
                    });

                    menuModal.hide();
                };

                menuModal.show();
            }
        });
    }

document.addEventListener('DOMContentLoaded', () => {
    const orderConfirmBtn = document.getElementById('orderConfirmBtn');
    if (orderConfirmBtn) {
        orderConfirmBtn.addEventListener('click', () => {
            alert('주문이 완료되었습니다!');
            Cart.items = [];
            Cart.updateCartView();

             // 주문 창 초기화
            document.querySelectorAll('input[name="toppings"]').forEach(input => {
                input.checked = false;
            });
            document.getElementById('quantity').value = 1;
            document.getElementById('napkin').checked = false;

            // 장바구니 및 오버레이 숨기기
            cartSidebar.classList.remove('show');
            cartOverlay.classList.remove('show');
            
        });
    }
});

    function detectAgeGroup() {
        const ageGroups = ['', 'elderly', 'child'];
        return ageGroups[Math.floor(Math.random() * ageGroups.length)];
    }


    function setupChildModeScroll() {
        const menuGrid = document.querySelector('.child .menu-grid');
        if (!menuGrid) return;

        let isScrolling = false;
        let startX;
        let scrollLeft;

        menuGrid.addEventListener('mousedown', handleDragStart);
        menuGrid.addEventListener('touchstart', handleDragStart);

        menuGrid.addEventListener('mousemove', handleDragMove);
        menuGrid.addEventListener('touchmove', handleDragMove);

        menuGrid.addEventListener('mouseup', handleDragEnd);
        menuGrid.addEventListener('mouseleave', handleDragEnd);
        menuGrid.addEventListener('touchend', handleDragEnd);

        function handleDragStart(e) {
            isScrolling = true;
            startX = e.type === 'touchstart' ? e.touches[0].pageX : e.pageX;
            scrollLeft = menuGrid.scrollLeft;
        }

        function handleDragMove(e) {
            if (!isScrolling) return;
            e.preventDefault();
            const x = e.type === 'touchmove' ? e.touches[0].pageX : e.pageX;
            const walk = (x - startX) * 2;
            menuGrid.scrollLeft = scrollLeft - walk;
        }

        function handleDragEnd() {
            isScrolling = false;
        }
    }

    function updateKioskUI() {
        const kiosk = document.getElementById('kiosk');
        const ageGroup = detectAgeGroup();

        kiosk.classList.remove('elderly', 'child');
        if (ageGroup) {
            kiosk.classList.add(ageGroup);

            if (ageGroup === 'child') {
                setupChildModeScroll();
            }
        }
    }
    document.addEventListener('DOMContentLoaded', updateKioskUI);
    setInterval(updateKioskUI, 5000);



    document.addEventListener('DOMContentLoaded', function () {
        const cartSidebar = document.getElementById('cartSidebar');
        const cartOverlay = document.querySelector('.cart-overlay');
        const orderButton = document.querySelector('.order-button');


        // menuOptionsModal 닫힘 시 오버레이 제거
        menuModalElement.addEventListener('hidden.bs.modal', () => {
            if (cartOverlay.classList.contains('show')) {
                cartOverlay.classList.remove('show'); // 오버레이 제거
            }
        });
        orderButton.addEventListener('click', function() {
            cartSidebar.classList.add('show');
            cartOverlay.classList.add('show');
        });

        // 장바구니 오버레이 클릭 시 닫기
        cartOverlay.addEventListener('click', function() {
            cartSidebar.classList.remove('show');
            cartOverlay.classList.remove('show');
        });


        const menuItems = document.querySelectorAll('.menu-item');
        menuItems.forEach(item => {
            item.addEventListener('click', function () {
                const menuName = this.querySelector('.card-title').textContent;
                const menuPrice = parseInt(this.querySelector('.card-text').textContent.replace('원', '').replace(',', ''));

                document.getElementById('menuOptionModalTitle').textContent = `${menuName} 옵션 선택`;

                const addToCartBtn = document.getElementById('addToCartBtn');
                addToCartBtn.onclick = null;
                addToCartBtn.onclick = function () {
                    const selectedToppings = Array.from(
                        document.querySelectorAll('input[name="toppings"]:checked')
                    ).map(el => el.nextElementSibling.textContent);

                    const quantity = document.getElementById('quantity').value;
                    const toppingPrice = Array.from(
                        document.querySelectorAll('input[name="toppings"]:checked')
                    ).reduce((sum, el) => sum + parseInt(el.value), 0);

                    const napkinPrice = document.getElementById('napkin').checked ? 100 : 0;
                    const totalPrice = (menuPrice + toppingPrice + napkinPrice) * quantity;

                    Cart.addItem({
                        name: menuName,
                        quantity: quantity,
                        toppings: selectedToppings,
                        totalPrice: totalPrice
                    });

                    new bootstrap.Modal(document.getElementById('menuOptionsModal')).hide();
                };

                new bootstrap.Modal(document.getElementById('menuOptionsModal')).show();
            });
        });
    });

    setInterval(function() {
        const adjustModalForAgeGroup = document.querySelector('script[data-adjust-modal]');
        if (adjustModalForAgeGroup) {
            adjustModalForAgeGroup.textContent = '';
        }
    }, 5000);




    function updateBannerDesign() {
        const kiosk = document.getElementById('kiosk');
        const ageGroup = detectAgeGroup(); // 기존 age group detection 함수 사용

        // 기존 배너 디자인 초기화
        const header = document.querySelector('.header');

        // 연령대별 특별 디자인 적용
        if (ageGroup === 'elderly') {
            header.classList.add('elderly');
        } else if (ageGroup === 'child') {
            header.classList.add('child');
        }
    }

    // 페이지 로드 시 및 주기적으로 배너 디자인 업데이트
    document.addEventListener('DOMContentLoaded', updateBannerDesign);
    setInterval(updateBannerDesign, 5000);

    document.getElementById('decreaseBtn').addEventListener('click', () => {
        const quantityInput = document.getElementById('quantity');
        let value = parseInt(quantityInput.value, 10);
        if (value > 1) {
            quantityInput.value = value - 1;
        }
    });
    
    document.getElementById('increaseBtn').addEventListener('click', () => {
        const quantityInput = document.getElementById('quantity');
        let value = parseInt(quantityInput.value, 10);
        quantityInput.value = value + 1;
    });
    
    document.addEventListener('DOMContentLoaded', () => {
        const menuModalElement = document.getElementById('menuOptionsModal');
        const cartOverlay = document.querySelector('.cart-overlay');
    
        // 모달 닫힘 이벤트 처리
        menuModalElement.addEventListener('hidden.bs.modal', () => {
            cartOverlay.classList.remove('show'); // 클릭 차단 오버레이 제거
        });
    
        // 주문 추가하기 버튼 클릭 이벤트
        document.getElementById('addToCartBtn').onclick = () => {
            const menuModal = bootstrap.Modal.getInstance(menuModalElement);
            menuModal.hide(); // 모달 닫기
            cartOverlay.classList.remove('show'); // 오버레이 제거
        };
    });
    
    
    