
console.log(bootstrap.Modal); // undefined가 출력되면 JS 파일 문제

const Cart = {
    items: [],
    addItem(item) {
        this.items.push(item);
        this.updateCartView();
    },
    generateOrderDetails() {
        return JSON.stringify({items: this.items});
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

const orderConfirmBtn = document.getElementById('orderConfirmBtn');
if (orderConfirmBtn) {
    orderConfirmBtn.addEventListener('click', async (e) => {
        e.preventDefault(); // 기본 폼 제출 동작 방지

        const orderDetails = Cart.generateOrderDetails();
        console.log(orderDetails);

        try {
            const response = await fetch('/page/order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: orderDetails,
            });

            if (response.ok) {
                alert('주문이 성공적으로 접수되었습니다!');
                Cart.items = []; // 장바구니 비우기
                Cart.updateCartView(); // 장바구니 UI 업데이트
            } else {
                alert('주문 처리 중 문제가 발생했습니다. 다시 시도해주세요.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('서버와의 통신 중 오류가 발생했습니다.');
        }
    });
}





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

async function fetchAgeGroup() {
    try {
        const response = await fetch('http://localhost:5000/result', {
            method: 'GET', // GET 요청으로 수정
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            const data = await response.json();
            return parseInt(data.result); // 서버에서 반환된 result 값을 정수로 변환 (0, 1, 2)
        } else {
            console.error('Error fetching age group:', response.statusText);
            return null;
        }
    } catch (error) {
        console.error('Error:', error);
        return null;
    }
}

async function updateKioskUI() {
    const kiosk = document.getElementById('kiosk');

    if (!kiosk) {
        console.error('Kiosk element not found');
        return;
    }

    const ageGroup = await fetchAgeGroup();

    if (ageGroup === null) {
        console.error('Failed to fetch age group');
        return;
    }

    // 템플릿 변경
    kiosk.classList.remove('elderly', 'child', 'adult');
    if (ageGroup === 0) {
        kiosk.classList.add('elderly'); // 노인 모드
    } else if (ageGroup === 1) {
        kiosk.classList.add('adult'); // 어른 모드
    } else if (ageGroup === 2) {
        kiosk.classList.add('child'); // 어린이 모드
        setupChildModeScroll(); // 어린이 모드에서 추가 설정 호출
    }
}

document.addEventListener('DOMContentLoaded', updateKioskUI);
setInterval(updateKioskUI, 5000);


/*function updateKioskUI() {
    const kiosk = document.getElementById('kiosk');
    const ageGroup = detectAgeGroup();

    kiosk.classList.remove('elderly', 'child');
    if (ageGroup) {
        kiosk.classList.add(ageGroup);

        if (ageGroup === 'child') {
            setupChildModeScroll();
        }
    }
}*/
/*document.addEventListener('DOMContentLoaded', updateKioskUI);
setInterval(updateKioskUI, 5000);*/



document.addEventListener('DOMContentLoaded', function () {
    const cartSidebar = document.getElementById('cartSidebar');
    const cartOverlay = document.querySelector('.cart-overlay');
    const orderButton = document.querySelector('.order-button');

    if (orderButton) {
        orderButton.addEventListener('click', function() {
            cartSidebar.classList.add('show');
            cartOverlay.classList.add('show');
        });
    }

    // 장바구니 오버레이 클릭 시 닫기
    cartOverlay.addEventListener('click', function() {
        cartSidebar.classList.remove('show');
        cartOverlay.classList.remove('show');
    });


    const menuItems = document.querySelectorAll('.menu-item');
    menuItems.forEach(item => {
        item.addEventListener('click', function () {
            const menuId = this.getAttribute('data-id');
            const menuName = this.querySelector('.card-title').textContent;
            const menuPrice = parseInt(this.querySelector('.card-text').textContent.replace('원', '').replace(',', ''));

            document.getElementById('menuOptionModalTitle').textContent = `${menuName} 옵션 선택`;

            const addToCartBtn = document.getElementById('addToCartBtn');
            addToCartBtn.onclick = null; // 기존 이벤트 핸들러 제거
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
                    menuId: menuId,
                    name: menuName,
                    quantity: quantity,
                    toppings: selectedToppings,
                    totalPrice: totalPrice
                });

                // 모달 닫기
                const menuModal = bootstrap.Modal.getInstance(document.getElementById('menuOptionsModal'));
                if (menuModal) {
                    menuModal.hide();
                }
            };

            // 모달 표시
            const menuModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('menuOptionsModal'));
            menuModal.show();
        });
    });
    ;
});



