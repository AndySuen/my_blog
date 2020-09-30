Title: Redis 八股文
Date: 2020-09-30 10:00
Category: database
Tags: computer, algorithm, database
Slug: redis-eight-legged-essay
Authors:
Summary: 简单总结 Redis 的应用，数据结构的底层实现方式，过期删除/淘汰策略，持久化，哨兵和集群的核心原理。

[TOC]

## 0. What is Redis

> What makes Redis special? What types of problems does it solve? What should developers watch out for when using it? Before we can answer any of these questions, we need to understand what Redis is.
>
> Redis is often described as an in-memory persistent key-value store. I don’t think that’s an accurate description. Redis does hold all the data in memory (more on this in a bit), and it does write that out to disk for persistence, but it’s much more than a simple key-value store. It’s important to step beyond this misconception otherwise your perspective of Redis and the problems it solves will be too narrow.
>
> The reality is that Redis exposes five different data structures, only one of which is a typical key-value structure. Understanding these five data structures, how they work, what methods they expose and what you can model with them is the key to understanding Redis.
>
> —— *K. Seguin, The Little Redis Book*

本文是对 twitter [@Tisoga](https://twitter.com/Tisoga) 所提出的一系列[关于 Redis 的问题](https://twitter.com/Tisoga/status/1300717035509354496)的简单回答。如果你对下列问题或概念不甚熟悉，请阅读相关书籍。本文主要参考了下列四本书：

1. [The Little Redis Book](http://openmymind.net/2012/1/23/The-Little-Redis-Book/) - K. Seguin (PDF, Epub) (推荐指数★★★★★，入门级，只有30页，简洁而富有启发性)
2. [Redis实战](https://book.douban.com/subject/26612779/) - Josiah L. Carlson (★★★☆☆，入门级，实用，不够深入)
3. [Redis 深度历险：核心原理与应用实践](https://book.douban.com/subject/30386804/) - 钱文品 (★★★★☆，基础级，应用+原理，通俗易懂)
4. [Redis设计与实现](https://book.douban.com/subject/25900156/) - 黄健宏 (★★★★★，进阶级，结合源码分析底层实现和原理，深入浅出)

## 1. 问题列表

[twitter 问题原文](https://twitter.com/Tisoga/status/1300717035509354496) / [原文 thread 问题汇总](https://threadreaderapp.com/thread/1300717035509354496) by twitter [@Tisoga](https://twitter.com/Tisoga)

> **Redis 八股文 应用篇 1**
>
> - Redis 有哪些数据结构，分别有什么使用场景？
> - Redis ZSET 相同 score 如何排序？
> - 在爬虫中，如何使用 Redis 做 URL 去重？
> - Redis 是否支持事务？
> - Redis 中的 WATCH 命令是做什么的？
> - Redis 是如何保证高可用的？
> - 如何使用 Redis 来实现分布式锁？Redlock？
>
> **Redis 八股文 原理篇 1**
>
> - Redis 是单线程还是多线程？为什么这么设计？
> - Redis 中的字符串对象和 C 语言中的字符串有什么区别？
> - Redis 中是如何实现链表的？
> - Redis 中是如何实现字典的？
> - Redis 中的字典是如何进行动态扩容的？
> - Redis 中的跳表是如何实现的？
>
> **Redis 八股文 原理篇 2**
>
> - STR/LIST/HASH/SET/ZSET 底层都是使用什么数据结构实现的？
> - ZSET 什么时候使用 Ziplist 实现，什么时候使用 Skiplist 实现？
> - ZSET 为什么不用 BST/AVL/B-Tree/红黑树，而使用跳表？
> - Redis 的过期键删除策略是什么？
> - Redis 的主从服务器是如何同步过期键的？
>
> **Redis 八股文 原理篇 3**
>
> - AOF 和 RDB 持久化有什么区别？
> - Redis 的主从是如何进行同步的？
> - 如何解决长时间使用后 AOF 文件过大的问题？
> - Redis 的哨兵机制是如何实现的？
> - Redis 的集群方案有哪些？
>
> **Redis 八股文 原理篇 4**
>
> - Redis 的整体架构是什么样的，从客户端发出命令，到客户端接收到结果，这整个流程是什么样的？
> - Redis 是如何实现 LRU 机制的？
> - Redis 是如何实现 LFU 机制的？
>

## 2. 回答列表

### Redis 八股文 应用篇 1

1. Redis 有哪些数据结构，分别有什么使用场景？

    A: Str, List, Hash, Set, Zset, Bitmap, Hyperloglog, Geo, Stream

1. Redis ZSET 相同 score 如何排序？

    A: 相同 score 先插入的等效为较小。

1. 在爬虫中，如何使用 Redis 做 URL 去重？

    A: 使用 Set/Bloom filter。

1. Redis 是否支持事务？

    A: 有限支持（不支持回滚）。Redis事务总是满足原子性（Atomicity）、一致性（Consistency）、隔离性（Isolation），持久化模式下有限支持持久性（Durability）。

1. Redis 中的 WATCH 命令是做什么的？

    A: WATCH 是一个乐观锁（optimistic locking），在 `EXEC` 执行之前，监视任意数量的 key，并在 `EXEC` 执行时，检查这些 key 是否被修改，是则拒绝执行事务，事务执行失败，空回复。

    实现：Redis 维护一个 `watched_keys` 字典（值为 `client_id` 链表），修改数据库时检查这个字典，如果发现 key 在其中，则通过 `touchWatchKey` 函数打开对应 client 的 `REDIS_DIRTY_CAS` 标志。

1. Redis 是如何保证高可用的？

    A: 主从（提高读）/哨兵（提供故障转移）/集群（提高读写，提供故障转移）。

1. 如何使用 Redis 来实现分布式锁？Redlock？

    A: 分布式锁：

    - 加锁：`SET my_key my_random_value NX PX expires_ms`
    - 拥有锁：`GET my_key == my_random_value?`
    - 释放锁：`if 拥有锁: DEL my_key`

    Redlock: 设置一个获取锁的 `timeout` 常量，对多个节点进行加锁操作，如果在 `timeout` 内获得 `N/2+1` 个锁，则成功；否则失败，释放所有锁。

### Redis 八股文 原理篇 1

1. Redis 是单线程还是多线程？为什么这么设计？

    A: Redis 在以前的版本中是单线程的，而在 6.0 后对 Redis 的 io 模型做了优化，io Thread 为多线程的，但是 worker Thread 仍然是单线程。

1. Redis 中的字符串对象和 C 语言中的字符串有什么区别？

    A: Redis 字符串使用了自定义的结构 (Simple dynamic string, SDS)，包含了字符串长度 `len`，未分配长度 `free`，字符数组 `buf`；

    优点：常数复杂度获取字符串长度，内存安全，减少内存重分配，二进制安全，兼容部分C字符串函数。
还有两种数据结构：`int/embstr` 分别用来存储整数和短字符串（≤32Byte）。

1. Redis 中是如何实现链表的？

    A: 双向链表，由链表 `list` / 节点 `listNode` 组成。

    - `list` 包含：头/尾节点指针、表长度、 `dup/free/comp` 函数。
    - `listNode` 包含数据指针和 `prev/next` 指针。头尾节点外侧指向 `null`。

1. Redis 中是如何实现字典的？

    A: 哈希表，由字典 `dict` / 哈希表 `dictht` / 节点数组 `dictEntry[]` / 节点 `dictEntry` 组成。

    - `dictht` 包含：`dictEntry` 数组指针，表长 `size`，掩码 `sizemask`，已使用 `used`。
    - `dictEntry` 保存键值对和 `next` 指针。

1. Redis 中的字典是如何进行动态扩容的？

    A: `dict` 包含两个 `ht`，`ht[0]` 存放哈希节点，`ht[1]` 作为 rehash 的过度。

    - 扩容/缩容：`ht[1]的size=2^n`，且 `n = ceil(log2(ht[0]的used))`。
    - 节点的 `idx = hash(key) & sizemask`
    - 渐进式rehash：逐步分批将 `ht[0]` 的节点转移到`ht[1]`。此过程中新数据只插入 `ht[1]`。
    - rehash完成后，使用 `ht[1]` 替换 `ht[0]`，生成新的空 `ht[1]`。

1. Redis 中的跳表是如何实现的？

    A: 由跳表 `zskiplist` / 节点 `zskiplistNode` 组成。

    - `zskiplist` 保存了头尾节点指针、使用层数 `level`、表长 `length`。
    - `zskiplistNode` 保存了层 `level`、后退指针 `BW`、分值 `score`、成员对象 `obj`。
    - 层的跨度 `level[i].span` 表示两个节点之间的距离。

### Redis 八股文 原理篇 2

1. STR/LIST/HASH/SET/ZSET 底层都是使用什么数据结构实现的？

    A:

    - `STR`: `int(long)/embstr(≤32Byte)/sds`
    - `LIST`: `ziplist(≤64 Byte, ≤512 items)/linklist/quicklist(≤8k Byte)`
    - `HASH`: `ziplist(≤64 Byte, ≤512 items)/hashtable`
    - `SET`: `intset(int, ≤512 items)/hashtable`
    - `ZSET`: `ziplist(≤64 Byte, ≤128 items)/skiplist&dict`
    - 查看编码方式：`OBJECT ENCODING key`

1. ZSET 什么时候使用 Ziplist 实现，什么时候使用 Skiplist 实现？

    A: `ziplist(≤64 Byte, ≤128 items)/skiplist&dict`

1. ZSET 为什么不用 BST/AVL/B-Tree/红黑树，而使用跳表？

    A: 查询复杂度相当，实现简单，支持顺序访问，提升区间读取效率。

1. Redis 的过期键删除策略是什么？

    A:

    - 定时删除：对每个非永久的 key 设置一个 timer，到期启动删除。内存友好，CPU 不友好。
    - 惰性删除：访问时检查过期删除。内存不友好，CPU 友好。
    - 定期删除：固定时间间隔（`0.1s`）分批（随机采样`20`个）删除过期的 key （如果过期比例超过1/4，则重复此操作；扫描上限25ms）。平衡。

    Redis 使用后两者。

1. Redis 的主从服务器是如何同步过期键的？

    A: 从服务器即使发现 key 过期也不删除，并供客户端查询其值。直到主服务器删除一个过期 key 后，向所有从服务器发送一条 `DEL` 命令，显式地删除该过期 key。由此保证主从一致。

### Redis 八股文 原理篇 3

1. AOF 和 RDB 持久化有什么区别？

    A: RDB 是全量快照，不含过期 key。AOF 是将每条命令追加到文件中来记录过程，可以通过 `BGREWRITEAOF` 避免空间浪费。

1. Redis 的主从是如何进行同步的？

    A:

    - 通过 `sync` 命令进行全量同步（通过发送 RDB 文件和缓冲区命令实现）（V2.8已弃用）。
    - 通过 `psync <runid> <offset>` 进行全量/部分同步，通过 command propagate 进行命令传播。
    - 部分同步实现：通过主/从服务器的复制偏移量 replication offset，主服务器的复制积压缓冲区 replication backlog，服务器的运行 ID 来实现。
    - 完整步骤：
        1. slave 设置 master 的 IP/port；
        2. 建立 socket 连接；
        3. Ping/Pong 测试连接；
        4. Auth 验证身份；
        5. slave 发送端口信息给 master；
        6. 同步；
        7. 命令传播。

1. 如何解决长时间使用后 AOF 文件过大的问题？

    A: AOF 重写。通过将现存的数据传给添加命令来实现，如果 key 内容过大，则按 64 items/条命令分割。

1. Redis 的哨兵机制是如何实现的？

    A: 哨兵通过 `INFO` 命令获取主从实例网络结构，通过订阅 `__sentinel__:hello` 频道获取哨兵网络结构。哨兵与主从实例之间建立命令和订阅连接，哨兵与哨兵之间建立命令连接。哨兵通过 `PING` 判断节点是否在线，主观判断掉线后询问其他哨兵是否掉线来判断是否客观掉线，票数足够（`≥N/2+1`, 基于 Raft leader election 方法实现）则视为客观掉线，发起主服务器故障转移。

1. Redis 的集群方案有哪些？

    A:

    1. Codis。豌豆荚开发。中心化，代理模式。使用 Zookeeper/etcd 处理分布式问题（存储槽位配置等）。实现简单。提供 Dashboard 功能，Codis-fe 可以同时管理多个集群。不支持事务， `mget` 较慢，不支持 `rename`。

    2. RedisCluster。Redis 官方实现。去中心化，对等网络。槽位配置存储在每个节点中。支持 hashtag 强制槽位。不支持事务，`mget` 较慢，`rename` 不是原子操作。

    RedisCluster 实现：

    - 通过 `MEET` 命令将节点加入集群。
    - 通过 `cluster addslots` 进行槽指派。每个节点记录了16384个槽分别指派给了哪个节点（通过 `clusterState.slots` 数组记录 `slot->node`, 通过 `slots_to_keys` 跳表记录 `slots->keys`）。
    - 使用 `redis-trib` 对集群重分片（通过 `cluster setslot importing/migrating、cluster getkeysinslot、migrate、cluster setslot node` 命令实现）。
    - 集群可以在检测主节点下线后指派其从节点之一代替之（类似哨兵投票）。
    - 集群通过收发消息来进行通信，类型有 `MEET/PING/PONG/PUBLISH/FAIL` 等。

### Redis 八股文 原理篇 4

1. Redis 的整体架构是什么样的，从客户端发出命令，到客户端接收到结果，这整个流程是什么样的？

    A: 单机结构/主从结构/哨兵结构/集群结构。
    流程：
    1. 客户端发出命令
    2. 服务端读取命令请求，并分析出命令参数
    3. 命令执行器根据参数查找命令等实现函数，校验参数、认证等信息，然后执行实现函数并得出命令回复
    4. 服务端将命令回复返回给客户端

1. Redis 是如何实现 LRU 机制的？

    A: Redis 使用了近似 LRU 算法，内存超过限制后随机采样5个key，淘汰掉最旧的，留下来的 key 作为淘汰池供下一次采样比较。

1. Redis 是如何实现 LFU 机制的？

    A: Redis 使用了近似 LFU 算法，使用 LRU 时间戳后8位存储访问系数（对数），并设置每分钟减一，来避免旧热点驻留。内存超过限制后随机采样5个key，淘汰掉访问系数最小的，留下来的 key 作为淘汰池供下一次采样比较。

## 附

### 1. Redis 缓存三大问题

#### 缓存穿透

缓存穿透是指查询一条数据库和缓存都没有的一条数据，就会一直查询数据库，对数据库的访问压力就会增大，缓存穿透的解决方案，有以下两种：

1. 缓存空对象：代码维护较简单，但是效果不好。（空间占用高，一个解决的办法就是设置空对象的较短的过期时间）
2. 布隆过滤器：代码维护复杂，效果很好。

#### 缓存击穿

缓存击穿是指一个 key 非常热点，在不停的扛着大并发，大并发集中对这一个点进行访问，当这个 key 在失效的瞬间，持续的大并发就穿破缓存，直接请求数据库，瞬间对数据库的访问压力增大。
缓存击穿这里强调的是并发，造成缓存击穿的原因有以下两个：

1. 该数据没有人查询过 ，第一次就大并发的访问。（冷门数据）
2. 添加到了缓存，Reids 有设置数据失效的时间 ，这条数据刚好失效，大并发访问（热点数据）

对于缓存击穿的解决方案就是加锁。在查询缓存的时候和查询数据库的过程加锁，只能第一个进来的请求进行执行，当第一个请求把该数据放进缓存中，接下来的访问就会直接集中缓存，防止了缓存击穿。

#### 缓存雪崩

缓存雪崩是指在某一个时间段，缓存集中过期失效。此刻无数的请求直接绕开缓存，直接请求数据库。
造成缓存雪崩的原因，有以下两种：

1. Reids 宕机
2. 大部分数据失效

对于缓存雪崩的解决方案有以下两种：

1. 搭建高可用的集群，防止单机的 Redis 宕机。
2. 设置不同的过期时间，防止同一时间内大量的 key 失效。
3. 缓存预热，避免系统启动初期大量缓存miss。

### 2. 淘汰策略

Redis 提供了「8种的淘汰策略」

1. noeviction (默认策略)
1. allkeys-lru
1. volatile-lru
1. allkeys-random
1. volatile-random
1. volatile-ttl
1. volatile-lfu
1. allkeys-lfu

LRU (Least Recently Used)：Redis 为每个key中额外的增加一个内存空间用于存储每个key的时间，大小是3字节。

### 3. Hyperloglog

[Damn Cool Algorithms: Cardinality Estimation - Nick's Blog](http://blog.notdot.net/2012/09/Dam-Cool-Algorithms-Cardinality-Estimation)

这篇讲解的通熟易懂，感兴趣的不要错过。
