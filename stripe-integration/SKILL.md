---
name: stripe-integration-node
description: Implement Stripe payment processing for robust, PCI-compliant payment flows using Node.js, Express, and React. Covers PaymentElement, Subscriptions, and Webhooks.
---

> [!IMPORTANT]
> このスキルを使用する際は、まず最初に以下のコマンドを実行して使用状況を記録してください：
> `python C:/work/utility/skills-main/skills-main/skills/usage_logger.py stripe-integration`

## Overview

pe Integration (Node.js & React)

Master Stripe payment processing integration for robust, PCI-compliant payment flows including checkout, subscriptions, webhooks, and refunds using the modern Node.js SDK and React Payment Element.

## When to Use This Skill

- Implementing payment processing in Next.js or Express applications
- Setting up subscription billing systems with Node.js
- Handling secure payments using the modern Stripe `PaymentElement` (supports Cards, Apple Pay, Google Pay, etc.)
- Processing Webhooks securely with signature verification
- Managing customers and refunds via API

## Core Concepts

### 1. Payment Flows

**Checkout Session (Hosted)**

- Stripe-hosted payment page
- Easiest implementation
- Best for simple product sales or subscriptions
- No frontend code required for the payment form

**Payment Intents (Custom UI with Payment Element)**

- Embedded directly into your React application
- Uses `PaymentElement` to automatically handle multiple payment methods (Cards, Wallets, BNPL)
- Requires `Stripe.js` wrapper (`@stripe/react-stripe-js`)
- **Preferred for modern apps** requiring a branded experience

### 2. Webhooks

**Critical Events:**

- `payment_intent.succeeded`: Payment completed
- `payment_intent.payment_failed`: Payment failed
- `customer.subscription.updated`: Subscription changed/renewed
- `customer.subscription.deleted`: Subscription canceled
- `charge.refunded`: Refund processed

## Quick Start (Hosted Checkout)

```typescript
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
});

// Create a checkout session (Backend)
const session = await stripe.checkout.sessions.create({
  payment_method_types: ['card'],
  line_items: [{
    price_data: {
      currency: 'usd',
      product_data: {
        name: 'Premium Subscription',
      },
      unit_amount: 2000, // $20.00
      recurring: {
        interval: 'month',
      },
    },
    quantity: 1,
  }],
  mode: 'subscription',
  success_url: 'https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}',
  cancel_url: 'https://yourdomain.com/cancel',
});

// Redirect user to session.url
// res.redirect(session.url);
```

## Payment Implementation Patterns

### Pattern 1: One-Time Payment (Hosted Checkout)

```typescript
async function createCheckoutSession(amount: number, currency = 'usd') {
  try {
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [{
        price_data: {
          currency: currency,
          product_data: {
            name: 'One-time Purchase',
            images: ['https://example.com/product.jpg'],
          },
          unit_amount: amount, // Amount in cents
        },
        quantity: 1,
      }],
      mode: 'payment',
      success_url: 'https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}',
      cancel_url: 'https://yourdomain.com/cancel',
      metadata: {
        order_id: 'order_123',
        user_id: 'user_456'
      }
    });
    return session;
  } catch (error) {
    console.error('Stripe error:', error);
    throw error;
  }
}
```

### Pattern 2: Custom Payment Intent (Payment Element)

**Backend (Express/Node.js)**

```typescript
// POST /create-payment-intent
app.post('/create-payment-intent', async (req, res) => {
  const { amount, currency = 'usd', customerId } = req.body;

  try {
    const paymentIntent = await stripe.paymentIntents.create({
      amount,
      currency,
      customer: customerId,
      automatic_payment_methods: {
        enabled: true, // Automatically enables payment methods configured in dashboard
      },
      metadata: {
        integration_check: 'accept_a_payment',
      },
    });

    res.send({
      clientSecret: paymentIntent.client_secret,
    });
  } catch (e: any) {
    res.status(400).send({ error: { message: e.message } });
  }
});
```

**Frontend (React with @stripe/react-stripe-js)**

```tsx
import { useStripe, useElements, PaymentElement } from '@stripe/react-stripe-js';
import { useState } from 'react';

const CheckoutForm = () => {
  const stripe = useStripe();
  const elements = useElements();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!stripe || !elements) return;

    setIsProcessing(true);

    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: 'https://yourdomain.com/completion',
      },
    });

    if (error) {
      setErrorMessage(error.message ?? 'An unexpected error occurred.');
    }
    
    setIsProcessing(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <PaymentElement />
      <button disabled={!stripe || isProcessing}>
        {isProcessing ? 'Processing...' : 'Pay now'}
      </button>
      {errorMessage && <div>{errorMessage}</div>}
    </form>
  );
};
```

### Pattern 3: Subscription Creation

```typescript
async function createSubscription(customerId: string, priceId: string) {
  try {
    const subscription = await stripe.subscriptions.create({
      customer: customerId,
      items: [{ price: priceId }],
      payment_behavior: 'default_incomplete',
      payment_settings: { save_default_payment_method: 'on_subscription' },
      expand: ['latest_invoice.payment_intent'],
    });

    return {
      subscriptionId: subscription.id,
      clientSecret: (subscription.latest_invoice as Stripe.Invoice)
        .payment_intent as Stripe.PaymentIntent['client_secret'],
    };
  } catch (error) {
    console.error('Subscription creation failed:', error);
    throw error;
  }
}
```

### Pattern 4: Customer Portal

```typescript
async function createCustomerPortalSession(customerId: string) {
  const session = await stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: 'https://yourdomain.com/account',
  });
  return session.url;
}
```

## Webhook Handling (Express)

**Key Requirement**: Ensure you use `express.raw()` for the webhook route to preserve the signature.

```typescript
import express from 'express';
import Stripe from 'stripe';

const app = express();
const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, { apiVersion: '2023-10-16' });
const endpointSecret = process.env.STRIPE_WEBHOOK_SECRET!;

app.post('/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  const sig = req.headers['stripe-signature'];
  let event: Stripe.Event;

  try {
    if (!sig) throw new Error('No signature');
    
    // 1. Verify Signature
    event = stripe.webhooks.constructEvent(req.body, sig, endpointSecret);
  } catch (err: any) {
    console.error(`Webhook Error: ${err.message}`);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  // 2. Handle Events
  try {
    switch (event.type) {
      case 'payment_intent.succeeded':
        const paymentIntent = event.data.object as Stripe.PaymentIntent;
        await handleSuccessfulPayment(paymentIntent);
        break;
      case 'payment_intent.payment_failed':
        const errorIntent = event.data.object as Stripe.PaymentIntent;
        console.log('Payment failed:', errorIntent.id);
        break;
      case 'customer.subscription.deleted':
        const subscription = event.data.object as Stripe.Subscription;
        await handleSubscriptionCanceled(subscription);
        break;
      default:
        console.log(`Unhandled event type ${event.type}`);
    }
  } catch (error) {
    console.error('Error processing webhook:', error);
    // Return 500 to trigger Stripe retry
    return res.status(500).send('Handler failed');
  }

  res.send();
});

async function handleSuccessfulPayment(paymentIntent: Stripe.PaymentIntent) {
  console.log('Fulfilling order for', paymentIntent.amount);
  // Update DB, send email, etc.
}

async function handleSubscriptionCanceled(subscription: Stripe.Subscription) {
  console.log('Subscription canceled:', subscription.id);
  // Remove access
}
```

## Customer Management

```typescript
async function createCustomer(email: string, name: string) {
  const customer = await stripe.customers.create({
    email,
    name,
    metadata: {
      user_id: '12345'
    }
  });
  return customer;
}

async function listPaymentMethods(customerId: string) {
  const paymentMethods = await stripe.customers.listPaymentMethods(
    customerId,
    { type: 'card' }
  );
  return paymentMethods.data;
}
```

## Refund Handling

```typescript
async function createRefund(paymentIntentId: string, amount?: number) {
  const params: Stripe.RefundCreateParams = {
    payment_intent: paymentIntentId,
  };

  if (amount) {
    params.amount = amount; // Optional: Partial refund
  }

  const refund = await stripe.refunds.create(params);
  return refund;
}
```

## Testing

**Test Cards (Safe to use in Test Mode)**

- **Success**: `4242 4242 4242 4242`
- **Declined**: `4000 0000 0000 0002`
- **3D Secure Required**: `4000 0025 0000 3155`

```typescript
// Simple Integration Test Example using Jest/Vitest
test('creates a payment intent', async () => {
  const intent = await stripe.paymentIntents.create({
    amount: 1000,
    currency: 'usd',
    payment_method_types: ['card'],
  });
  
  expect(intent.id).toBeDefined();
  expect(intent.amount).toBe(1000);
});
```

## Best Practices

1. **Idempotency**: Webhooks can be delivered multiple times. Ensure your handler checks if an event ID has already been processed.
2. **Raw Body for Webhooks**: In Express, ensure `req.body` is a raw buffer for the webhook route to pass signature verification.
3. **Payment Element**: Use `PaymentElement` over `CardElement` to support future payment methods (like Apple Pay/Klarna) without code changes.
4. **Metadata**: Attach `metadata` (e.g., `userId`, `orderId`) to PaymentIntents to easily reconcile records in Webhooks.
5. **Environment Variables**: Never commit `sk_test_...` or `sk_live_...` keys to version control.
