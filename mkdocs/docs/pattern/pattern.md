# 设计模式

### 摘要

设计模式不是圣经。它只是之前的开发者在进行面向对象开发时候，为了达到提高代码复用率，解耦各模块联系，最小化修改等目的，抽象出的一系列较常用的开发经验。尽管这些经验思路上具有一定的普遍意义，但是具体在不同语言之间的呈现还是会有不小差异，甚至有些在 C++/JAVA 这类静态语言里适用的模式，在 python 这种动态语言里已经失去了原有的价值。

本章节的目的不旨在对各类模式的介绍上，仅对平时用刀过的一些模式进行一定的总结。

### 设计模式分类

#### 创建型
```
Simple Factory  （简单工厂）
Factory Method  （工厂方法）
Abstract Factory（抽象工厂）
Builder         （建造者）
Prototype       （原型）
Singleton       （单例）
```

#### 结构型
```
Adapter Class/Object（适配器）
Bridge              （桥接）
Composite           （组合）
Decorator           （装饰）
Facade              （外观）
Flyweight           （享元）
Proxy               （代理）
```

#### 行为型
```
Interpreter            （解释器）
Template Method        （模板方法）
Chain of Responsibility（责任链）
Command                （命令）
Iterator               （迭代器）
Mediator               （中介者）
Memento                （备忘录）
Observer               （观察者）
State                  （状态）
Strategy               （策略）
Visitor                （访问者）
```