// 主脚本文件
// 创建Vue应用
const app = Vue.createApp({
    data() {
        return {
            isLoggedIn: false,
            isAdmin: false,
            currentUser: null,
            toastMessage: '',
            toastTitle: '',
            toastClass: ''
        };
    },
    mounted() {
        // 检查用户登录状态
        this.checkLoginStatus();
    },
    methods: {
        // 检查用户登录状态
        async checkLoginStatus() {
            try {
                const response = await axios.get('/api/auth/profile');
                if (response.data.success) {
                    this.isLoggedIn = true;
                    this.currentUser = response.data.user;
                    this.isAdmin = this.currentUser.role === 'admin';
                }
            } catch (error) {
                console.log('未登录或会话已过期');
                this.isLoggedIn = false;
                this.currentUser = null;
                this.isAdmin = false;
            }
        },
        
        // 退出登录
        async logout() {
            try {
                const response = await axios.post('/api/auth/logout');
                if (response.data.success) {
                    this.isLoggedIn = false;
                    this.currentUser = null;
                    this.isAdmin = false;
                    this.showToast('成功', '已退出登录', 'success');
                    // 跳转到首页
                    this.$router.push('/');
                }
            } catch (error) {
                this.showToast('错误', '退出登录失败', 'error');
            }
        },
        
        // 显示通知提示
        showToast(title, message, type = 'info') {
            this.toastTitle = title;
            this.toastMessage = message;
            this.toastClass = type;
            
            const toastEl = this.$refs.toast;
            const toast = new bootstrap.Toast(toastEl);
            toast.show();
        }
    }
});

// 定义组件

// 首页组件
const Home = {
    template: `
        <div class="container">
            <div class="jumbotron bg-light p-5 rounded">
                <h1 class="display-4">欢迎来到重庆师范大学师能素质协会</h1>
                <p class="lead">这是我们协会的活动报名平台，您可以浏览和报名参加各种特精彩活动。</p>
                <hr class="my-4">
                <p>立即加入我们，参与丰富多彩的校园活动！</p>
                <a class="btn btn-primary btn-lg" href="/activities">浏览活动</a>
            </div>
            
            <h2 class="mt-5 mb-4">最新活动</h2>
            <div class="row" v-if="activities.length > 0">
                <div class="col-md-4 mb-4" v-for="activity in activities" :key="activity.id">
                    <div class="card activity-card">
                        <img :src="activity.image_url || '/static/img/default-activity.jpg'" class="card-img-top activity-image" alt="活动图片">
                        <div class="card-body">
                            <h5 class="card-title">{{ activity.title }}</h5>
                            <p class="card-text">{{ truncateText(activity.description, 100) }}</p>
                        </div>
                        <div class="card-footer">
                            <small class="text-muted">活动时间: {{ formatDate(activity.start_time) }}</small>
                            <a :href="'/activities/' + activity.id" class="btn btn-sm btn-outline-primary float-end">查看详情</a>
                        </div>
                    </div>
                </div>
            </div>
            <div class="text-center py-5" v-else>
                <p>暂无活动</p>
            </div>
        </div>
    `,
    data() {
        return {
            activities: []
        };
    },
    mounted() {
        this.fetchActivities();
    },
    methods: {
        async fetchActivities() {
            try {
                const response = await axios.get('/api/activities/?status=active');
                if (response.data.success) {
                    this.activities = response.data.activities;
                }
            } catch (error) {
                console.error('获取活动列表失败:', error);
            }
        },
        truncateText(text, length) {
            if (!text) return '';
            return text.length > length ? text.substring(0, length) + '...' : text;
        },
        formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }
};

// 活动列表组件
const ActivityList = {
    template: `
        <div class="container">
            <h2 class="mb-4">活动列表</h2>
            <div class="row">
                <div class="col-md-4 mb-4" v-for="activity in activities" :key="activity.id">
                    <div class="card h-100">
                        <img :src="activity.image_url || '/static/img/default-activity.jpg'" class="card-img-top" alt="活动图片">
                        <div class="card-body">
                            <h5 class="card-title">{{ activity.title }}</h5>
                            <p class="card-text">{{ truncateText(activity.description, 100) }}</p>
                        </div>
                        <div class="card-footer">
                            <small class="text-muted">活动时间: {{ formatDate(activity.start_time) }}</small>
                            <a :href="'/activities/' + activity.id" class="btn btn-sm btn-outline-primary float-end">查看详情</a>
                        </div>
                    </div>
                </div>
            </div>
            <div class="text-center py-5" v-if="activities.length === 0">
                <p>暂无活动</p>
            </div>
        </div>
    `,
    data() {
        return {
            activities: []
        };
    },
    mounted() {
        this.fetchActivities();
    },
    methods: {
        async fetchActivities() {
            try {
                const response = await axios.get('/api/activities/');
                if (response.data.success) {
                    this.activities = response.data.activities;
                }
            } catch (error) {
                console.error('获取活动列表失败:', error);
            }
        },
        truncateText(text, length) {
            if (!text) return '';
            return text.length > length ? text.substring(0, length) + '...' : text;
        },
        formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }
};

// 活动详情组件
const ActivityDetail = {
    template: `
        <div class="container" v-if="activity">
            <div class="row">
                <div class="col-md-8">
                    <h2 class="mb-3">{{ activity.title }}</h2>
                    <img :src="activity.image_url || '/static/img/default-activity.jpg'" class="img-fluid rounded mb-4" alt="活动图片">
                    <div class="card mb-4">
                        <div class="card-body">
                            <h5 class="card-title">活动详情</h5>
                            <p class="card-text">{{ activity.description }}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">活动信息</h5>
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item">开始时间: {{ formatDate(activity.start_time) }}</li>
                                <li class="list-group-item">结束时间: {{ formatDate(activity.end_time) }}</li>
                                <li class="list-group-item">地点: {{ activity.location }}</li>
                                <li class="list-group-item">组织者: {{ activity.organizer }}</li>
                                <li class="list-group-item">状态: {{ getStatusText(activity.status) }}</li>
                            </ul>
                        </div>
                        <div class="card-footer">
                            <button class="btn btn-primary w-100" @click="registerActivity" 
                                    :disabled="activity.status !== 'active' || isRegistered">
                                {{ isRegistered ? '已报名' : '立即报名' }}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="container text-center py-5" v-else>
            <p>加载中...</p>
        </div>
    `,
    data() {
        return {
            activity: null,
            isRegistered: false,
            activityId: null
        };
    },
    mounted() {
        // 从URL获取活动ID
        const pathParts = window.location.pathname.split('/');
        this.activityId = pathParts[pathParts.length - 1];
        
        if (this.activityId) {
            this.fetchActivityDetail();
            this.checkRegistrationStatus();
        }
    },
    methods: {
        async fetchActivityDetail() {
            try {
                const response = await axios.get(`/api/activities/${this.activityId}`);
                if (response.data.success) {
                    this.activity = response.data.activity;
                }
            } catch (error) {
                console.error('获取活动详情失败:', error);
                app.showToast('错误', '获取活动详情失败', 'error');
            }
        },
        async checkRegistrationStatus() {
            if (!app.isLoggedIn) return;
            
            try {
                const response = await axios.get(`/api/activities/${this.activityId}/registration`);
                this.isRegistered = response.data.registered;
            } catch (error) {
                console.error('检查报名状态失败:', error);
            }
        },
        async registerActivity() {
            if (!app.isLoggedIn) {
                app.showToast('提示', '请先登录', 'warning');
                return;
            }
            
            try {
                const response = await axios.post(`/api/activities/${this.activityId}/register`);
                if (response.data.success) {
                    this.isRegistered = true;
                    app.showToast('成功', '报名成功', 'success');
                }
            } catch (error) {
                console.error('报名失败:', error);
                app.showToast('错误', error.response?.data?.message || '报名失败', 'error');
            }
        },
        formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        getStatusText(status) {
            const statusMap = {
                'draft': '草稿',
                'active': '进行中',
                'completed': '已结束',
                'cancelled': '已取消'
            };
            return statusMap[status] || status;
        }
    }
};

// 管理员控制面板组件
const AdminDashboard = {
    template: `
        <div class="container" v-if="isAdmin">
            <h2 class="mb-4">管理员控制面板</h2>
            <div class="row">
                <div class="col-md-3 mb-4">
                    <div class="list-group">
                        <a href="#" class="list-group-item list-group-item-action" 
                           :class="{ active: activeTab === 'activities' }"
                           @click.prevent="activeTab = 'activities'">
                            活动管理
                        </a>
                        <a href="#" class="list-group-item list-group-item-action" 
                           :class="{ active: activeTab === 'users' }"
                           @click.prevent="activeTab = 'users'">
                            用户管理
                        </a>
                        <a href="#" class="list-group-item list-group-item-action" 
                           :class="{ active: activeTab === 'registrations' }"
                           @click.prevent="activeTab = 'registrations'">
                            报名管理
                        </a>
                    </div>
                </div>
                <div class="col-md-9">
                    <!-- 活动管理 -->
                    <div v-if="activeTab === 'activities'">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h3>活动管理</h3>
                            <a href="/activities/new" class="btn btn-primary">新建活动</a>
                        </div>
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>标题</th>
                                        <th>开始时间</th>
                                        <th>状态</th>
                                        <th>操作</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="activity in activities" :key="activity.id">
                                        <td>{{ activity.id }}</td>
                                        <td>{{ activity.title }}</td>
                                        <td>{{ formatDate(activity.start_time) }}</td>
                                        <td>{{ getStatusText(activity.status) }}</td>
                                        <td>
                                            <div class="btn-group btn-group-sm">
                                                <a :href="'/activities/' + activity.id" class="btn btn-info">查看</a>
                                                <a :href="'/activities/' + activity.id + '/edit'" class="btn btn-warning">编辑</a>
                                                <button @click="deleteActivity(activity.id)" class="btn btn-danger">删除</button>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <!-- 用户管理 -->
                    <div v-if="activeTab === 'users'">
                        <h3>用户管理</h3>
                        <div class="table-responsive">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>用户名</th>
                                        <th>邮箱</th>
                                        <th>角色</th>
                                        <th>操作</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="user in users" :key="user.id">
                                        <td>{{ user.id }}</td>
                                        <td>{{ user.username }}</td>
                                        <td>{{ user.email }}</td>
                                        <td>{{ user.role }}</td>
                                        <td>
                                            <div class="btn-group btn-group-sm">
                                                <button @click="toggleUserRole(user.id)" class="btn btn-warning">
                                                    {{ user.role === 'admin' ? '取消管理员' : '设为管理员' }}
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <!-- 报名管理 -->
                    <div v-if="activeTab === 'registrations'">
                        <h3>报名管理</h3>
                        <div class="form-group mb-3">
                            <label for="activitySelect">选择活动</label>
                            <select id="activitySelect" class="form-control" v-model="selectedActivityId" @change="fetchRegistrations">
                                <option value="">-- 请选择活动 --</option>
                                <option v-for="activity in activities" :key="activity.id" :value="activity.id">
                                    {{ activity.title }}
                                </option>
                            </select>
                        </div>
                        <div class="table-responsive" v-if="selectedActivityId">
                            <table class="table table-striped">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>用户名</th>
                                        <th>邮箱</th>
                                        <th>报名时间</th>
                                        <th>操作</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="reg in registrations" :key="reg.id">
                                        <td>{{ reg.id }}</td>
                                        <td>{{ reg.user.username }}</td>
                                        <td>{{ reg.user.email }}</td>
                                        <td>{{ formatDate(reg.created_at) }}</td>
                                        <td>
                                            <button @click="cancelRegistration(reg.id)" class="btn btn-sm btn-danger">取消报名</button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                            <div class="text-center py-3" v-if="registrations.length === 0">
                                <p>暂无报名记录</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="container text-center py-5" v-else>
            <p>您没有权限访问此页面</p>
        </div>
    `,
    data() {
        return {
            activeTab: 'activities',
            activities: [],
            users: [],
            registrations: [],
            selectedActivityId: '',
            isAdmin: app.isAdmin
        };
    },
    mounted() {
        // 确保用户是管理员
        if (this.isAdmin) {
            this.fetchActivities();
            this.fetchUsers();
        } else {
            console.log('非管理员用户尝试访问控制面板');
        }
    },
    methods: {
        async fetchActivities() {
            try {
                const response = await axios.get('/api/admin/activities');
                if (response.data.success) {
                    this.activities = response.data.activities;
                }
            } catch (error) {
                console.error('获取活动列表失败:', error);
                app.showToast('错误', '获取活动列表失败', 'error');
            }
        },
        async fetchUsers() {
            try {
                const response = await axios.get('/api/admin/users');
                if (response.data.success) {
                    this.users = response.data.users;
                }
            } catch (error) {
                console.error('获取用户列表失败:', error);
                app.showToast('错误', '获取用户列表失败', 'error');
            }
        },
        async fetchRegistrations() {
            if (!this.selectedActivityId) return;
            
            try {
                const response = await axios.get(`/api/admin/activities/${this.selectedActivityId}/registrations`);
                if (response.data.success) {
                    this.registrations = response.data.registrations;
                }
            } catch (error) {
                console.error('获取报名列表失败:', error);
                app.showToast('错误', '获取报名列表失败', 'error');
            }
        },
        async deleteActivity(activityId) {
            if (!confirm('确定要删除此活动吗？此操作不可撤销。')) return;
            
            try {
                const response = await axios.delete(`/api/admin/activities/${activityId}`);
                if (response.data.success) {
                    app.showToast('成功', '活动已删除', 'success');
                    this.fetchActivities();
                }
            } catch (error) {
                console.error('删除活动失败:', error);
                app.showToast('错误', '删除活动失败', 'error');
            }
        },
        async toggleUserRole(userId) {
            try {
                const user = this.users.find(u => u.id === userId);
                const newRole = user.role === 'admin' ? 'user' : 'admin';
                
                const response = await axios.put(`/api/admin/users/${userId}/role`, { role: newRole });
                if (response.data.success) {
                    app.showToast('成功', `用户角色已更新为${newRole === 'admin' ? '管理员' : '普通用户'}`, 'success');
                    this.fetchUsers();
                }
            } catch (error) {
                console.error('更新用户角色失败:', error);
                app.showToast('错误', '更新用户角色失败', 'error');
            }
        },
        async cancelRegistration(registrationId) {
            if (!confirm('确定要取消此报名记录吗？')) return;
            
            try {
                const response = await axios.delete(`/api/admin/registrations/${registrationId}`);
                if (response.data.success) {
                    app.showToast('成功', '报名记录已取消', 'success');
                    this.fetchRegistrations();
                }
            } catch (error) {
                console.error('取消报名失败:', error);
                app.showToast('错误', '取消报名失败', 'error');
            }
        },
        formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        getStatusText(status) {
            const statusMap = {
                'draft': '草稿',
                'active': '进行中',
                'completed': '已结束',
                'cancelled': '已取消'
            };
            return statusMap[status] || status;
        }
    }
};

// 活动表单组件
const ActivityForm = {
    template: `
        <div class="container">
            <h2 class="mb-4">{{ isEditing ? '编辑活动' : '创建活动' }}</h2>
            <form @submit.prevent="submitForm">
                <div class="mb-3">
                    <label for="title" class="form-label">活动标题</label>
                    <input type="text" class="form-control" id="title" v-model="activity.title" required>
                </div>
                <div class="mb-3">
                    <label for="description" class="form-label">活动描述</label>
                    <textarea class="form-control" id="description" rows="5" v-model="activity.description" required></textarea>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="start_time" class="form-label">开始时间</label>
                        <input type="datetime-local" class="form-control" id="start_time" v-model="activity.start_time" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label for="end_time" class="form-label">结束时间</label>
                        <input type="datetime-local" class="form-control" id="end_time" v-model="activity.end_time" required>
                    </div>
                </div>
                <div class="mb-3">
                    <label for="location" class="form-label">活动地点</label>
                    <input type="text" class="form-control" id="location" v-model="activity.location" required>
                </div>
                <div class="mb-3">
                    <label for="organizer" class="form-label">组织者</label>
                    <input type="text" class="form-control" id="organizer" v-model="activity.organizer" required>
                </div>
                <div class="mb-3">
                    <label for="status" class="form-label">活动状态</label>
                    <select class="form-control" id="status" v-model="activity.status" required>
                        <option value="draft">草稿</option>
                        <option value="active">进行中</option>
                        <option value="completed">已结束</option>
                        <option value="cancelled">已取消</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label for="image" class="form-label">活动图片URL</label>
                    <input type="text" class="form-control" id="image" v-model="activity.image_url">
                    <small class="form-text text-muted">可选，留空将使用默认图片</small>
                </div>
                <div class="d-flex justify-content-between">
                    <button type="button" class="btn btn-secondary" @click="goBack">取消</button>
                    <button type="submit" class="btn btn-primary">{{ isEditing ? '更新' : '创建' }}</button>
                </div>
            </form>
        </div>
    `,
    data() {
        return {
            activity: {
                title: '',
                description: '',
                start_time: '',
                end_time: '',
                location: '',
                organizer: '',
                status: 'draft',
                image_url: ''
            },
            isEditing: false,
            activityId: null
        };
    },
    mounted() {
        // 检查是否为编辑模式
        const pathParts = window.location.pathname.split('/');
        if (pathParts.includes('edit')) {
            this.isEditing = true;
            this.activityId = pathParts[pathParts.length - 2]; // URL格式: /activities/:id/edit
            this.fetchActivityDetail();
        }
        
        // 确保用户是管理员
        if (!app.isAdmin) {
            app.showToast('错误', '您没有权限执行此操作', 'error');
            window.location.href = '/';
        }
    },
    methods: {
        async fetchActivityDetail() {
            try {
                const response = await axios.get(`/api/activities/${this.activityId}`);
                if (response.data.success) {
                    // 格式化日期时间为HTML datetime-local格式
                    const activity = response.data.activity;
                    activity.start_time = this.formatDateTimeForInput(activity.start_time);
                    activity.end_time = this.formatDateTimeForInput(activity.end_time);
                    this.activity = activity;
                }
            } catch (error) {
                console.error('获取活动详情失败:', error);
                app.showToast('错误', '获取活动详情失败', 'error');
            }
        },
        async submitForm() {
            try {
                let response;
                if (this.isEditing) {
                    response = await axios.put(`/api/admin/activities/${this.activityId}`, this.activity);
                } else {
                    response = await axios.post('/api/admin/activities', this.activity);
                }
                
                if (response.data.success) {
                    app.showToast('成功', `活动已${this.isEditing ? '更新' : '创建'}`, 'success');
                    // 跳转到活动详情页
                    const activityId = this.isEditing ? this.activityId : response.data.activity.id;
                    window.location.href = `/activities/${activityId}`;
                }
            } catch (error) {
                console.error(`${this.isEditing ? '更新' : '创建'}活动失败:`, error);
                app.showToast('错误', `${this.isEditing ? '更新' : '创建'}活动失败`, 'error');
            }
        },
        formatDateTimeForInput(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            return date.toISOString().slice(0, 16); // 格式: YYYY-MM-DDTHH:MM
        },
        goBack() {
            window.history.back();
        }
    }
};

// 注册组件
app.component('home-page', Home);
app.component('activity-list', ActivityList);
app.component('activity-detail', ActivityDetail);
app.component('admin-dashboard', AdminDashboard);
app.component('activity-form', ActivityForm);

// 创建路由
const routes = [
    { path: '/', component: Home },
    { path: '/activities', component: ActivityList },
    { path: '/activities/:id', component: ActivityDetail },
    { path: '/admin/dashboard', component: AdminDashboard },
    { path: '/activities/new', component: ActivityForm },
    { path: '/activities/:id/edit', component: ActivityForm }
];

const router = VueRouter.createRouter({
    history: VueRouter.createWebHistory(),
    routes
});

app.use(router);

// 挂载应用
app.mount('#app');
