"""Модуль с классом Product для представления товара на складе."""

from dataclasses import dataclass, field


@dataclass
class Product:
    """Товар на складе.

    Атрибуты:
        id: Уникальный идентификатор товара.
        name: Наименование товара.
        article: Артикул товара.
        category: Категория товара.
        unit: Единица измерения (шт., кг и т.п.).
        price: Цена за единицу товара.
        stock: Текущий остаток на складе.
    """

    id: int
    name: str
    article: str
    category: str
    unit: str
    price: float
    stock: int = field(default=0)

    def __str__(self) -> str:
        """Строковое представление товара для вывода."""
        return (
            f"[{self.id}] {self.name} (арт. {self.article}): "
            f"{self.stock} {self.unit}, категория: {self.category}"
        )

    def check_availability(self, quantity: int = 1) -> tuple[bool, str]:
        """Проверить, достаточно ли товара на складе.

        Args:
            quantity: Требуемое количество товара.

        Returns:
            Кортеж (доступен, сообщение).
        """
        if self.stock >= quantity:
            return True, "Товар доступен"
        return False, f"Недостаточно товара. Остаток: {self.stock} {self.unit}."

    def receive(self, quantity: int) -> tuple[bool, str]:
        """Принять товар на склад (увеличить остаток).

        Args:
            quantity: Количество для приёмки (должно быть > 0).

        Returns:
            Кортеж (успех, сообщение).
        """
        if quantity <= 0:
            return False, "Количество должно быть положительным числом"
        self.stock += quantity
        return True, f"Принято: +{quantity} {self.unit}. Новый остаток: {self.stock} {self.unit}."

    def ship(self, quantity: int) -> tuple[bool, str]:
        """Отгрузить товар со склада (уменьшить остаток).

        Args:
            quantity: Количество для отгрузки (должно быть > 0).

        Returns:
            Кортеж (успех, сообщение).
        """
        available, message = self.check_availability(quantity)
        if not available:
            return False, message
        self.stock -= quantity
        return True, f"Отгружено: -{quantity} {self.unit}. Новый остаток: {self.stock} {self.unit}."

    def get_total_value(self) -> float:
        """Рассчитать общую стоимость остатков товара."""
        return self.stock * self.price

    def get_info(self) -> dict:
        """Вернуть подробную информацию о товаре."""
        available, status_message = self.check_availability()
        return {
            "id": self.id,
            "name": self.name,
            "article": self.article,
            "stock": self.stock,
            "price": self.price,
            "total_value": self.get_total_value(),
            "status": status_message,
        }

    def to_dict(self) -> dict:
        """Преобразовать объект в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "article": self.article,
            "category": self.category,
            "unit": self.unit,
            "price": self.price,
            "stock": self.stock,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        """Создать объект Product из словаря (при загрузке из JSON).

        Args:
            data: Словарь с полями товара.

        Returns:
            Экземпляр Product.
        """
        return cls(
            id=data["id"],
            name=data["name"],
            article=data["article"],
            category=data["category"],
            unit=data["unit"],
            price=float(data["price"]),
            stock=int(data.get("stock", 0)),
        )