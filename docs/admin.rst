.. _picbed-admin:

===========
站点管理
===========

此为管理员的控制台配置说明，在这里可以全局设置、钩子管理等，配置项含义基本
上是简单明了，根据提示即可，下面仅说明部分重点或复杂配置。

1. 系统设置
-------------

全局设置，包括网站本身、上传细节、钩子配置。

1.1 站点设置
===============

- CORS Origin

  设置允许跨域的源站（关于CORS请参考 `Mozilla官方文档 <https://developer.mozilla.org/docs/Web/HTTP/Access_control_CORS>`_ ）

  源站格式：http[s]://domain.name
  
  不同端口不同协议均属于不同源，可以用英文逗号分隔多个！

  允许使用 **\*** 表示允许所有源，此时不可以有其他内容！

  .. tip::

    LinkToken中所用的origin是此处的子集

1.2 上传设置
==============

- 上传字段

  定义通过POST表单获取图片数据的字段，默认字段是picbed，如不明白，请勿修改！

- 存储后端

  选择保存图片的扩展钩子，本地、又拍云、GitHub等，至少有一个，否则无法保存
  图片。


1.3 钩子设置
=============

此处有模板中钩子插入点，内置与第三方钩子可以通过hooksetting定义表单，
管理员进行配置。

2. 钩子扩展
---------------

2.1 安装第三方包
===================

调用pip命令，安装pypi上的包，或者直接安装诸如git、svn上的模块。

注意，此功能仅仅是安装（到用户家目录下），并不会加载到程序中。

2.2 添加第三方钩子
=====================

将第三方包加载到程序中，作为钩子扩展功能点。
